from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.models import Lessons, Courses, Words, Phrases
from utils.handle_upload_text_file import group_by_para_or_sentence
import json
import traceback
import math
from django.contrib.auth.decorators import login_required

def get_dict_status(user):
    words_qs = Words.objects.filter(user = user)
    phrases_qs = Phrases.objects.filter(user = user)
    status_word_dict = {w.word_key : w.word_status for w in words_qs}
    status_phrase_dict = {ph.phrase : ph.phrase_status for ph in phrases_qs}
    list_all_phrases = [phrase.split() for phrase in status_phrase_dict.keys()]
    return status_word_dict, status_phrase_dict, list_all_phrases


def get_lesson_sets(lesson_obj,  list_all_phrases):
    found_phrases = []
    with lesson_obj.text_file.open('r') as f:
        data = json.load(f)
        list_ref = data["list_ref"]
        list_id = data["list_id"]

    list_words_in_lesson = []
    for word_idx,  item in enumerate(list_id):
        list_words_in_lesson.append({
            "word": list_ref[word_idx],
            "s_idx": item[2]
        })
    group_by_sentence = group_by_para_or_sentence(list_words_in_lesson, 's_idx')

    # Filter phrase in this text
    for items_in_sentence in group_by_sentence:
        sentence_list = [item['word'] for item in items_in_sentence]
        for phrase_list in list_all_phrases:
            if len(sentence_list) < len(phrase_list) :
                continue
            
            for i in range(len(sentence_list) - len(phrase_list) + 1):
                if sentence_list[i : i + len(phrase_list)] == phrase_list:
                    found_phrases.append(phrase_list)
                    break


    set_words = set(list_ref)
    set_phrases = set(' '.join(phrase_list) for phrase_list in found_phrases)

    total_words = len(list_ref)
    return set_words, set_phrases, total_words



def caculate_specification(set_words, set_phrases, status_word_dict, status_phrase_dict):
    number_newwords = sum(1 for w in set_words if w not in status_word_dict)
    number_lingq = sum(1 for w in set_words if 0 < status_word_dict.get(w, 6) < 4 ) + sum(1 for p in set_phrases if status_phrase_dict.get(p) < 4)
    number_knownwords = sum(1 for w in set_words if 4<= status_word_dict.get(w, 0) ) + sum(1 for p in set_phrases if 4 <= status_phrase_dict.get(p) )
    newword_percents = math.ceil(number_newwords / len(set_words) * 100) if len(set_words)> 0 else 0
    return number_newwords, number_lingq, number_knownwords, newword_percents

@csrf_exempt
# @login_required
def get_data_cards(request):
    if request.method != 'GET':
        return JsonResponse({'message' : 'Invalid request !'}, status = 405)
    try:
        print("✅ PATH:", request.path)
        print("✅ AUTH:", request.user.is_authenticated, repr(request.user))
        print("✅ USER_ID:", getattr(request.user, "id", None))
        print("✅ USERNAME:", getattr(request.user, "username", None))
        print("✅ COOKIES:", dict(request.COOKIES))
        print("✅ SESSION_KEY:", request.session.session_key)

        if not request.user.is_authenticated:
            return JsonResponse({"message": "Not authenticated"}, status=401)

        # ... continue with your real logic here ...

    except Exception as e:
        print("🔥 ERROR:", repr(e))
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    # Get status dicts
    status_word_dict, status_phrase_dict, list_all_phrases = get_dict_status(request.user)

    twenty_last_opened_lessons = Lessons.objects.filter(course__user = request.user).order_by('-last_open_at')[:20]
    dataLessonCards = []
    for lesson_obj in twenty_last_opened_lessons:
        set_words, set_phrases, total_words = get_lesson_sets(lesson_obj,  list_all_phrases)

        # Caculate lesson specifications
    
        number_newwords, number_lingq, number_knownwords, newword_percents = caculate_specification(set_words, set_phrases, status_word_dict, status_phrase_dict)

        list_lesson_names = list(
            Lessons.objects.filter(course = lesson_obj.course)
            .order_by("id").values_list('lesson_name', flat=True)
        )
        lesson_number = list_lesson_names.index(lesson_obj.lesson_name) + 1
        
        lesson_img_url = None
        if lesson_obj.lesson_img_file:
            lesson_img_url = request.build_absolute_uri(lesson_obj.lesson_img_file.url)
        dataLessonCards.append ({
            "imgUrl": lesson_img_url,
            "courseName": lesson_obj.course.course_name,
            'lessonNumber': lesson_number,
            'lessonName': lesson_obj.lesson_name,
            'numberNewWords': number_newwords,
            'numberLingQs': number_lingq,
            'numberKnownWords': number_knownwords,
            'newWordsPercents': newword_percents,
            "numberTotalWords" : total_words,
            "numberUniqueWords" : len(set_words)
        })

    # Caculate course specifications
    twenty_last_opened_courses = [course for course in Courses.objects.filter(user = request.user).order_by("-last_open_at") if Lessons.objects.filter(course = course).count() >0][:20]
    dataCourseCards = []
    for course_obj in twenty_last_opened_courses:
        sum_word_set, sum_phrase_set, sum_total_words  = set(), set(), 0
        lessons_in_course = Lessons.objects.filter(course = course_obj)
        for lesson_obj in lessons_in_course:
            word_set, phrase_set, total_words = get_lesson_sets(lesson_obj, list_all_phrases)
            sum_word_set = sum_word_set | word_set
            sum_phrase_set = sum_phrase_set | phrase_set
            sum_total_words += total_words

        number_lessons = lessons_in_course.count() 
        number_newwords, number_lingq, number_knownwords, newword_percents = caculate_specification(sum_word_set, sum_phrase_set, status_word_dict, status_phrase_dict)

        cousre_img_url = None
        if course_obj.course_img_file:
            cousre_img_url = request.build_absolute_uri(course_obj.course_img_file.url)
        dataCourseCards.append({
            # "imgUrl" : course_obj.course_img_file.url,
            "imgUrl" : cousre_img_url,  
            'numberLessons': number_lessons,
            'courseName': course_obj.course_name,
            'numberNewWords': number_newwords,
            'numberLingQs': number_lingq,
            'numberKnownWords': number_knownwords,
            'newWordsPercents': newword_percents,
            'numberTotalWords' : sum_total_words,
            "numberUniqueWords" : len(sum_word_set)
        })

    return JsonResponse({
        "dataLessonCards" : dataLessonCards,
        "dataCourseCards" : dataCourseCards
    })


@csrf_exempt
@login_required
def get_list_courses(request):
    if request.method != 'GET':
        return JsonResponse({'message' : 'Invalid request!'}, status = 405)
    
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    course_objs = Courses.objects.filter(user = request.user)
    list_course  = []
    for course in course_objs:
        name = course.course_name
        url = '/images/course.jpg'
        if course.course_img_file:
            url = request.build_absolute_uri(course.course_img_file.url)
        list_course.append({
            'name': name,
            'url': url
        })
    print('list_course', list_course)

    return JsonResponse({
        'listCourse' : list_course
    }, status = 200)

@csrf_exempt
@login_required
def show_course_infos(request):
    if request.method != 'GET':
        return JsonResponse({'message' : 'Invalid request!'}, status = 405)
    
    course_name = request.GET.get("course_name", '').strip()

    if not course_name:
        return JsonResponse({'message' : 'Missing course name!'}, status = 400)
    
    status_word_dict, status_phrase_dict, list_all_phrases = get_dict_status(request.user)

    course_obj = Courses.objects.get(user = request.user, course_name = course_name)

    lesson_objs = Lessons.objects.filter(course = course_obj).order_by('id')

    dataLessonCards = []
    sum_word_set , sum_phrase_set, sum_total_words = set(), set(), 0
    for lessonNumber,  lesson_obj in enumerate(lesson_objs):
        set_words, set_phrases, total_words = get_lesson_sets(lesson_obj, list_all_phrases)
        sum_word_set = sum_word_set | set_words
        sum_phrase_set = sum_phrase_set | set_phrases
        sum_total_words += total_words

        number_newwords, number_lingq, number_knownwords, newword_percents = caculate_specification(set_words, set_phrases, status_word_dict, status_phrase_dict)
        lesson_img_url = None
        if lesson_obj.lesson_img_file:
            lesson_img_url = request.build_absolute_uri(lesson_obj.lesson_img_file.url)
        dataLessonCards.append ({
            "imgUrl": lesson_img_url,
            "courseName": lesson_obj.course.course_name,
            'lessonNumber': lessonNumber +1,
            'lessonName': lesson_obj.lesson_name,
            'numberNewWords': number_newwords,
            'numberLingQs': number_lingq,
            'numberKnownWords': number_knownwords,
            'newWordsPercents': newword_percents,
            "numberTotalWords": total_words,
            "numberUniqueWords" : len(set_words)

        })
    
    number_newwords, number_lingq, number_knownwords, newword_percents = caculate_specification(sum_word_set , sum_phrase_set, status_word_dict, status_phrase_dict)
    course_img_url = None
    if course_obj.course_img_file:
        course_img_url= request.build_absolute_uri(course_obj.course_img_file.url)
    dataCourseCard= {
            # "imgUrl" : course_obj.course_img_file.url,
            "imgUrl" : course_img_url,  
            'numberLessons': lesson_objs.count(),
            'courseName': course_obj.course_name,
            'numberNewWords': number_newwords,
            'numberLingQs': number_lingq,
            'numberKnownWords': number_knownwords,
            'newWordsPercents': newword_percents,
            'numberTotalWords' : sum_total_words, 
            'numberUniqueWords': len(sum_word_set)
        }
    
    return JsonResponse({
        "dataCourseCard" : dataCourseCard,
        "dataLessonCards" : dataLessonCards
    }) 



    



