from typing import List, Tuple, Optional
from utils.extract_data import  get_lists_txt, get_lists_whisper
import json


# ============================================================
# 1. Needleman–Wunsch alignment between reference and Whisper tokens
# ============================================================

def nw_ref_match_flags(
    ref: List[str], whisper: List[str]
) -> List[Tuple[str, int, Optional[int]]]:
    """
    Perform Needleman–Wunsch alignment between reference tokens and Whisper tokens.

    Returns a list of tuples: (ref_word, match_flag, whisper_index)
        - match_flag = 1 if match, 0 if mismatch
        - whisper_index = index of matched whisper word, None if not matched
    """

    # Scoring constants
    MATCH, MISMATCH, GAP = 1, -1, -1
    n, m = len(ref), len(whisper)

    # Initialize dynamic programming and backtrace matrices
    dp = [[0] * (m + 1) for _ in range(n + 1)]     # DP table for alignment scores
    bt = [[None] * (m + 1) for _ in range(n + 1)]  # Backtrace table: 'D', 'U', 'L'

    # Initialize first row/column with gap penalties
    for i in range(1, n + 1):
        dp[i][0] = dp[i - 1][0] + GAP
        bt[i][0] = 'U'
    for j in range(1, m + 1):
        dp[0][j] = dp[0][j - 1] + GAP
        bt[0][j] = 'L'

    # Fill DP table with alignment scores
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Calculate scores for diagonal, up, and left moves
            score_diag = dp[i - 1][j - 1] + (MATCH if ref[i - 1] == whisper[j - 1] else MISMATCH)
            score_up = dp[i - 1][j] + GAP
            score_left = dp[i][j - 1] + GAP

            best = max(score_diag, score_up, score_left)

            # Tie-breaking priority: diagonal > up > left
            if best == score_diag:
                dp[i][j], bt[i][j] = score_diag, 'D'
            elif best == score_up:
                dp[i][j], bt[i][j] = score_up, 'U'
            else:
                dp[i][j], bt[i][j] = score_left, 'L'

    # Backtrace to reconstruct alignment path
    aligned_ref, aligned_wh, aligned_widx = [], [], []
    i, j = n, m
    while i > 0 or j > 0:
        move = bt[i][j] if (i >= 0 and j >= 0) else None
        if i > 0 and j > 0 and move == 'D':
            # Match or mismatch
            aligned_ref.append(ref[i - 1])
            aligned_wh.append(whisper[j - 1])
            aligned_widx.append(j - 1)
            i -= 1
            j -= 1
        elif i > 0 and (j == 0 or move == 'U'):
            # Deletion (gap in whisper)
            aligned_ref.append(ref[i - 1])
            aligned_wh.append(None)
            aligned_widx.append(None)
            i -= 1
        else:
            # Insertion (gap in reference)
            aligned_ref.append(None)
            aligned_wh.append(whisper[j - 1])
            aligned_widx.append(j - 1)
            j -= 1

    # Reverse the alignments since we built them backwards
    aligned_ref.reverse()
    aligned_wh.reverse()
    aligned_widx.reverse()

    # Build final list of match flags per reference word
    result = []
    for r_tok, w_tok, w_idx in zip(aligned_ref, aligned_wh, aligned_widx):
        if r_tok is None:
            continue
        if w_tok is not None and r_tok == w_tok:
            result.append((r_tok, 1, w_idx))  # Match
        else:
            result.append((r_tok, 0, None))   # Mismatch / missing
    return result


# ============================================================
# 2. Compute sentence-level timestamps from word timestamps
# ============================================================

def Get_timestamp(words_in_the_same_para):
    """
    Compute start and end timestamps for each sentence.

    Args:
        words_in_the_same_para (list): list of lists of word objects grouped by sentence.

    Returns:
        list[dict]: each dict contains {start, end, text, p_idx}
    """
    timestamp_sentence_level = []

    for words in words_in_the_same_para:
        # Combine words to reconstruct sentence text
        sentence_text = " ".join([w["word"] for w in words])
        p_idx = words[0]["p_idx"]

        # Find first and last word that has valid timestamp
        first_non_null = next((w for w in words if w["has_timestamp"]), None)
        final_non_null = next((w for w in reversed(words) if w["has_timestamp"]), None)

        # If no timestamps found → mark as None
        if not first_non_null or not final_non_null:
            start = end = None
        else:
            start = round(first_non_null["start"], 2)
            end = round(final_non_null["end"], 2)

        timestamp_sentence_level.append({
            "start": start,
            "end": end,
            "text": sentence_text,
            "p_idx": p_idx
        })
        # print(f"start: {str(start):<6} - end: {str(end):<6} | {sentence_text}")

    return timestamp_sentence_level


# ============================================================
# 3. Group words by paragraph index or sentence index
# ============================================================

def group_by_para_or_sentence(timestamp_word_level, group_type):
    """
    Group words by paragraph ('p_idx') or sentence ('s_idx') index.

    Args:
        timestamp_word_level (list): list of word objects with indexes
        group_type (str): key to group by ('p_idx' or 's_idx')

    Returns:
        list[list]: nested list of grouped words
    """
    words_in_the_same_type = []
    current_object = []
    current_idx = 0

    for word in timestamp_word_level:
        # Continue same group if index matches
        if word[group_type] == current_idx:
            current_object.append(word)
        else:
            # Start a new group
            words_in_the_same_type.append(current_object)
            current_idx = word[group_type]
            current_object = [word]

    if current_object:
        words_in_the_same_type.append(current_object)

    return words_in_the_same_type


# ============================================================
# 4. End-to-end process: Compute sentence timestamps from text + whisper
# ============================================================

def get_sentence_timestamp(txt_path, whisper_path):
    """
    Generate sentence-level timestamps by aligning text with Whisper output.

    Steps:
        1. Load and preprocess text and whisper data.
        2. Run Needleman–Wunsch alignment.
        3. Generate word-level timestamps (direct + interpolated).
        4. Group words by paragraph/sentence.
        5. Compute final sentence-level timestamps.
    """
    list_ref, list_id = get_lists_txt(txt_path)
    whisper_wordtimestamp, whisper = get_lists_whisper(whisper_path)

    # Step 1: Align reference tokens with Whisper tokens
    needleman_result = nw_ref_match_flags(list_ref, whisper)

    # Step 2: Assign timestamps at word level
    timestamp_word_level = []
    for i, item in enumerate(list_id):
        word, p_idx, s_idx, idx_in_s = item
        matched_flag, matched_whisper_idx = needleman_result[i][1], needleman_result[i][2]

        if matched_flag == 1:
            # Directly aligned word → copy Whisper timestamps
            ts = whisper_wordtimestamp[matched_whisper_idx]
            timestamp_word_level.append({
                "word": word,
                "p_idx": p_idx,
                "s_idx": s_idx,
                "has_timestamp": True,
                "start": ts["start"],
                "end": ts["end"],
            })
        else:
            # No direct match → missing timestamp
            timestamp_word_level.append({
                "word": word,
                "p_idx": p_idx,
                "s_idx": s_idx,
                "has_timestamp": False,
                "start": None,
                "end": None,
            })

    # Step 3: Interpolate timestamps for missing words
    consecutive_nulls_idx = []
    i = 0
    while i < len(timestamp_word_level):
        start = i
        end = i
        if not timestamp_word_level[i]["has_timestamp"]:
            while i + 1 < len(timestamp_word_level) and not timestamp_word_level[i + 1]["has_timestamp"]:
                i += 1
                end = i
            consecutive_nulls_idx.append((start, end))
        i += 1

    # Fill gaps by linear interpolation between known timestamps
    for first_null, final_null in consecutive_nulls_idx:
        if first_null > 0 and final_null < len(timestamp_word_level) - 1:
            start_time = timestamp_word_level[first_null - 1]["end"]
            end_time = timestamp_word_level[final_null + 1]["start"]

            number_nulls = final_null - first_null + 1
            gap = (end_time - start_time) / number_nulls

            # Assign interpolated timestamps
            for j in range(number_nulls):
                word_obj = timestamp_word_level[first_null + j]
                word_obj["has_timestamp"] = True
                word_obj["start"] = start_time + j * gap
                word_obj["end"] = start_time + (j + 1) * gap

    # Step 4: Group by paragraph → then by sentence
    timestamp_word_level_group_by_para = group_by_para_or_sentence(timestamp_word_level, "p_idx")
    timestamp_word_level_group_para_sentence = [
        group_by_para_or_sentence(item, "s_idx") for item in timestamp_word_level_group_by_para
    ]

    # Step 5: Derive sentence-level timestamps
    timestamp_result = [Get_timestamp(item) for item in timestamp_word_level_group_para_sentence]
    return timestamp_result, list_id


# ============================================================
# 5. CLI entry point for quick testing
# ============================================================

if __name__ == "__main__":
    i = 1  # test file index
    txt_path = f"test/test{i}.txt"
    whisper_path = f"test/result{i}.json"

    print(f"Processing test file {i} ...")
    timestamp_result = get_sentence_timestamp(txt_path, whisper_path)

    # Save results to JSON for inspection
    with open("checkaudio.json", "w", encoding="utf-8") as file:
        json.dump(timestamp_result, file, indent=2)


