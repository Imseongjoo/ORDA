from django.shortcuts import render, redirect
from django.views.generic import DetailView, ListView
from django.contrib.gis.serializers.geojson import Serializer
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import *
import json, os, urllib.request, time, requests, datetime, math
from datetime import date, datetime, timedelta
from urllib.parse import urlencode, quote_plus, unquote
from django.db.models import F, Count, When, Case
from django.conf import settings
from .forms import ReviewCreationForm
from django.contrib.auth.decorators import login_required
# Create your views here.


class MountainListView(ListView):
    template_name = 'mountains/mountain_list.html'
    context_object_name = 'mountains'
    model = Mountain
    paginate_by = 12

    def get_queryset(self):
        sort_option = self.request.GET.get('sort', 'likes')  # 기본값으로 가나다순을 사용

        if sort_option == 'likes':
            queryset = Mountain.objects.order_by('-likes')  # 좋아요순으로 정렬
        elif sort_option == 'reviews':
            queryset = Mountain.objects.order_by('-reviews_count')  # 리뷰 개수순으로 정렬
        elif sort_option == 'id':
            queryset = Mountain.objects.order_by('id')  # 가나다순으로 정렬
        elif sort_option == 'views':
            queryset = Mountain.objects.order_by('-views')  # 조회순으로 정렬
        elif sort_option == 'height':
            queryset = Mountain.objects.order_by('height') # 고도순으로 정렬
        else:
            queryset = Mountain.objects.all()  # 기본적으로 모든 데이터 조회

        return queryset


class MountainDetailView(DetailView):
    template_name = 'mountains/mountain_detail.html'
    context_object_name = 'mountain'
    model = Mountain

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        Mountain.objects.filter(pk=self.object.pk).update(views=F('views') + 1)

        context = self.get_context_data(object=self.object)
        context.update(self.news())
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 산관련
        mountain = self.get_object()
        serializer = Serializer()
        courses = mountain.course_set.all()
        course_details = {}
        for course in courses:
            geojson_data = serializer.serialize(CourseDetail.objects.filter(crs_name_detail=course), fields=('geom', 'is_waypoint', 'waypoint_name', 'crs_name_detail'))
            course_details[course.pk] =geojson_data

        # 리뷰 관련
        reviews = Review.objects.filter(mountain=mountain)



        # 기타
        now_weather_data = self.get_weather_forecast()
        print(now_weather_data)
        tem = now_weather_data['기온']
        hum = now_weather_data['습도']
        sky = now_weather_data['하늘상태']
        rain = now_weather_data['강수량']
        vec = now_weather_data['풍향']
        wsd = now_weather_data['풍속']
        now_time = now_weather_data['현재시각']

        sun = ['0700', '0800', '0900', '1000', '1100', '1200', '1300', '1400', '1500', '1600', '1700', '1800', '1900']
        moon = ['2000', '2100', '2200', '2300', '0000', '0100', '0200', '0300', '0400', '0500', '0600']
        
        air_data = self.get_air()
        def parse_data(data_str):
            parsed_data = {}
            entries = data_str.split(',')
            for entry in entries:
                key, value = entry.split(':')
                parsed_data[key.strip()] = value.strip()
            return parsed_data
        
        fine_dust = parse_data(air_data['미세먼지'])
        ozone = parse_data(air_data['오존'])

        fine_dust['서울특별시'] = fine_dust.pop('서울')
        fine_dust['제주도'] = fine_dust.pop('제주')
        fine_dust['전라남도'] = fine_dust.pop('전남')
        fine_dust['전라북도'] = fine_dust.pop('전북')
        fine_dust['광주광역시'] = fine_dust.pop('광주')
        fine_dust['경상남도'] = fine_dust.pop('경남')
        fine_dust['경상북도'] = fine_dust.pop('경북')
        fine_dust['울산광역시'] = fine_dust.pop('울산')
        fine_dust['대구광역시'] = fine_dust.pop('대구')
        fine_dust['부산광역시'] = fine_dust.pop('부산')
        fine_dust['충청남도'] = fine_dust.pop('충남')
        fine_dust['충청북도'] = fine_dust.pop('충북')
        fine_dust['세종특별자치시'] = fine_dust.pop('세종')
        fine_dust['대전광역시'] = fine_dust.pop('대전')
        fine_dust['강원도'] = fine_dust.pop('영동')
        fine_dust['경기도'] = fine_dust.pop('경기남부')
        fine_dust['인천광역시'] = fine_dust.pop('인천')

        ozone['서울특별시'] = ozone.pop('서울')
        ozone['제주도'] = ozone.pop('제주')
        ozone['전라남도'] = ozone.pop('전남')
        ozone['전라북도'] = ozone.pop('전북')
        ozone['광주광역시'] = ozone.pop('광주')
        ozone['경상남도'] = ozone.pop('경남')
        ozone['경상북도'] = ozone.pop('경북')
        ozone['울산광역시'] = ozone.pop('울산')
        ozone['대구광역시'] = ozone.pop('대구')
        ozone['부산광역시'] = ozone.pop('부산')
        ozone['충청남도'] = ozone.pop('충남')
        ozone['충청북도'] = ozone.pop('충북')
        ozone['세종특별자치시'] = ozone.pop('세종')
        ozone['대전광역시'] = ozone.pop('대전')
        ozone['강원도'] = ozone.pop('영동')
        ozone['경기도'] = ozone.pop('경기남부')
        ozone['인천광역시'] = ozone.pop('인천')


        split_region = (mountain.region).split()
        region = split_region[0]

        special_chars = [',', '/']
        for char in special_chars:
            if region.endswith(char):
                region = region[:-1]

        context = {
            # 산 관련
            'mountain': mountain,
            'courses': courses,
            'course_details': course_details,

            # 리뷰 관련
            'form': ReviewCreationForm(),
            'reviews': reviews,

            # 날씨
            'tem': tem,
            'hum': hum,
            'sky': sky,
            'rain': rain,
            'vec': vec,
            'wsd': wsd,
            'now_time': now_time,
            'sun': sun,
            'moon': moon,

            # 미세먼지, 오존
            'region': region,
            'fine_dust': fine_dust,
            'ozone': ozone,
        }
        # json_data = json.dumps(course_details, indent=4, sort_keys=True, ensure_ascii=False)
        # file_path = os.path.join(settings.STATICFILES_DIRS[0], 'course_details2.json')
        # with open(file_path, 'w', encoding='utf-8') as file:
        #     file.write(json_data)
        return context
    
    def news(self):
        client_id = 'ZsAfwEkHHvAjK1vzwLv1'
        client_secret = '6rMFVcImpz'
        query = self.get_object().name
        encText = urllib.parse.quote(query.encode('utf-8'))
        print(encText)

        result = []
        for start in range(1, 6, 1):
            url = f'https://openapi.naver.com/v1/search/news.json?query={encText}&display={start}&sort=sim'

            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id", client_id)
            request.add_header("X-Naver-Client-Secret", client_secret)
            response = urllib.request.urlopen(request)
            rescode = response.getcode()

            if rescode == 200:
                response_body = response.read().decode("utf-8")
                items = json.loads(response_body)["items"]
                for item in items:
                    item['title'] = item['title'].replace('&apos;', "'")
                    item['title'] = item['title'].replace('<b>', "")
                    item['title'] = item['title'].replace('</b>', "")
                result.extend(items)
                # result_set.update(json.loads(response_body)["items"])

            time.sleep(0.5)  # API 요청 간격을 조절하기 위해 0.5초 대기
        
        result = [dict(t) for t in {tuple(d.items()) for d in result}]

        return {
            'result': result,
        }
    
    def get_weather_forecast(self):
        mountain = self.get_object()
        # API 요청을 위한 URL과 파라미터 설정
        url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"

        serviceKey = "pY3s%2Fd1LhFkVDzZcyCuSavULc%2FJZVnzLRpdbmNUk6lD6Akcsw40HeR%2Bjop2DicS0L3UilYgnHE%2F8MKqMDTs2NQ%3D%3D"
        serviceKeyDecoded = unquote(serviceKey, 'UTF-8')

        now = datetime.now()
        today = datetime.today().strftime("%Y%m%d")
        y = date.today() - timedelta(days=1)
        yesterday = y.strftime("%Y%m%d")

        NX = 149            ## X축 격자점 수
        NY = 253            ## Y축 격자점 수

        Re = 6371.00877     ##  지도반경
        grid = 5.0          ##  격자간격 (km)
        slat1 = 30.0        ##  표준위도 1
        slat2 = 60.0        ##  표준위도 2
        olon = 126.0        ##  기준점 경도
        olat = 38.0         ##  기준점 위도
        xo = 210 / grid     ##  기준점 X좌표
        yo = 675 / grid     ##  기준점 Y좌표
        first = 0

        if first == 0 :
            PI = math.asin(1.0) * 2.0
            DEGRAD = PI/ 180.0
            
            re = Re / grid
            slat1 = slat1 * DEGRAD
            slat2 = slat2 * DEGRAD
            olon = olon * DEGRAD
            olat = olat * DEGRAD

            sn = math.tan(PI * 0.25 + slat2 * 0.5) / math.tan(PI * 0.25 + slat1 * 0.5)
            sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
            sf = math.tan(PI * 0.25 + slat1 * 0.5)
            sf = math.pow(sf, sn) * math.cos(slat1) / sn
            ro = math.tan(PI * 0.25 + olat * 0.5)
            ro = re * sf / math.pow(ro, sn)
            first = 1

        def mapToGrid(lat, lon, code = 0 ):
            ra = math.tan(PI * 0.25 + lat * DEGRAD * 0.5)
            ra = re * sf / pow(ra, sn)
            theta = lon * DEGRAD - olon
            if theta > PI :
                theta -= 2.0 * PI
            if theta < -PI :
                theta += 2.0 * PI
            theta *= sn
            x = (ra * math.sin(theta)) + xo
            y = (ro - ra * math.cos(theta)) + yo
            x = int(x + 1.5)
            y = int(y + 1.5)
            return x, y
        
        nx, ny = mapToGrid(mountain.geom.y, mountain.geom.x)

        if 0 < now.minute <= 59: # base_time와 base_date 구하는 함수
            if now.hour==0:
                base_time = "2330"
                base_date = yesterday
            else:
                pre_hour = now.hour-1
                if pre_hour < 10:
                    base_time = "0" + str(pre_hour) + "30"
                else:
                    base_time = str(pre_hour) + "30"
                base_date = today
        else:
            if now.hour < 10:
                base_time = "0" + str(now.hour-1) + "30"
            else:
                base_time = str(now.hour-1) + "30"
            base_date = today

        if now.hour < 10:
            now_time = '0'+str(now.hour)+'0'+'0'
        else:
            now_time = str(now.hour)+'0'+'0'

        queryParams = '?' + urlencode({ 
              quote_plus('serviceKey') : serviceKeyDecoded,
              quote_plus('base_date') : base_date, 
              quote_plus('base_time') : base_time,
              quote_plus('nx') : nx,
              quote_plus('ny') : ny,
              quote_plus('dataType') : 'json',
              quote_plus('numOfRows') : '1000'
              })

        # API 요청 보내기
        response = requests.get(url + queryParams, verify=False)
        items = response.json().get('response').get('body').get('items') #데이터들 아이템에 저장

        now_weather_data = dict()

        for item in items['item']:
            # 기온
            if item['category'] == 'T1H' and item['fcstDate'] == today and item['fcstTime'] == now_time:
                now_weather_data['기온'] = item['fcstValue']
            # 습도
            if item['category'] == 'REH' and item['fcstDate'] == today and item['fcstTime'] == now_time:
                now_weather_data['습도'] = item['fcstValue']
            # 하늘상태: 맑음(1) 구름많은(3) 흐림(4)
            if item['category'] == 'SKY' and item['fcstDate'] == today and item['fcstTime'] == now_time:
                now_weather_data['하늘상태'] = item['fcstValue']
            # 1시간 동안 강수량
            if item['category'] == 'RN1' and item['fcstDate'] == today and item['fcstTime'] == now_time:
                now_weather_data['강수량'] = item['fcstValue']
            # 풍향
            if item['category'] == 'VEC' and item['fcstDate'] == today and item['fcstTime'] == now_time:
                def get_direction(deg):
                    if '22.5' <= deg < '67.5':
                        return '북동'
                    elif '67.5' <= deg < '112.5':
                        return '동'
                    elif '112.5' <= deg < '157.5':
                        return '남동'
                    elif '157.5' <= deg < '202.5':
                        return '남'
                    elif '202.5' <= deg < '247.5':
                        return '남서'
                    elif '247.5' <= deg < '292.5':
                        return '서'
                    elif '292.5' <= deg < '337.5':
                        return '북서'
                    else:
                        return '북'
                now_weather_data['풍향'] = get_direction(item['fcstValue'])
            # 풍속
            if item['category'] == 'WSD' and item['fcstDate'] == today and item['fcstTime'] == now_time:
                now_weather_data['풍속'] = item['fcstValue']
            # 현재시각
            if item['fcstDate'] == today and item['fcstTime'] == now_time:
                now_weather_data['현재시각'] = now_time

        return now_weather_data

    def get_air(self):
        mountain = self.get_object()
        today = datetime.today().strftime("%Y-%m-%d")
        # API 요청을 위한 URL과 파라미터 설정
        url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMinuDustFrcstDspth"

        serviceKey = "pY3s%2Fd1LhFkVDzZcyCuSavULc%2FJZVnzLRpdbmNUk6lD6Akcsw40HeR%2Bjop2DicS0L3UilYgnHE%2F8MKqMDTs2NQ%3D%3D"
        serviceKeyDecoded = unquote(serviceKey, 'UTF-8')

        queryParams = '?' + urlencode({ 
              quote_plus('serviceKey') : serviceKeyDecoded,
              quote_plus('returnType') : 'json',
              quote_plus('numOfRows') : '100',
              quote_plus('searchDate') : today,
              quote_plus('InformCode') : 'PM10',
              })

        # API 요청 보내기
        response = requests.get(url + queryParams, verify=False)
        items = response.json().get('response').get('body').get('items') #데이터들 아이템에 저장
        formatted_items = json.dumps(items, indent=4, ensure_ascii=False)  # 데이터를 JSON 형식으로 깔끔하게 출력

        air = dict()

        for item in items:
            # 미세먼지
            if item['informCode'] == 'PM10' and item['informData'] == today:
                air['미세먼지'] = item['informGrade']
            # 오존
            if item['informCode'] == 'O3' and item['informData'] == today:
                air['오존'] = item['informGrade']

        return air



class CourseListView(ListView):
    template_name = 'mountains/course_list.html'
    context_object_name = 'courses'
    model = Course
    paginate_by = 5    

    def get_queryset(self):
        mountain_pk = self.kwargs['mountain_pk']
        mountain = Mountain.objects.get(pk=mountain_pk)
        sort_option = self.request.GET.get('sort', '')  # 정렬 옵션 가져오기

        queryset = Course.objects.filter(mntn_name=mountain)

        if sort_option == 'bookmarks':
            queryset = queryset.annotate(num_bookmarks=Count('bookmarks')).order_by('-num_bookmarks')
        elif sort_option == 'distance':
            queryset = queryset.order_by('distance')
        elif sort_option == 'hidden_time':
            queryset = queryset.order_by('hidden_time')
        elif sort_option == 'diff':
            # 난이도 정렬을 추가
            queryset = queryset.annotate(
                diff_order=Case(
                    When(diff='하', then=1),
                    When(diff='중', then=2),
                    When(diff='상', then=3),
                    default=4
                )
            ).order_by('diff_order')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mountain_pk = self.kwargs['mountain_pk']
        courses = self.get_queryset()
        mountain = Mountain.objects.get(pk=mountain_pk)
        sort_option = self.request.GET.get('sort', '')  # 정렬 옵션 가져오기

        serializer = Serializer()
        course_details = {}
        for course in courses:
            geojson_data = serializer.serialize(CourseDetail.objects.filter(crs_name_detail=course), fields=('geom', 'is_waypoint', 'waypoint_name', 'crs_name_detail'))
            course_details[course.pk] =geojson_data
        context = {
            'mountain': mountain,
            'courses': courses,
            'course_details': course_details
        }        
        return context        


class CourseAllListView(ListView):
    template_name = 'mountains/course_all_list.html'
    context_object_name = 'courses'
    model = Course

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_option = self.request.GET.get('sort', '')  # 기본값으로 전체

        if sort_option == 'bookmarks':
            queryset = queryset.annotate(bookmarks_count=Count('bookmarks'))
            queryset = queryset.order_by('-bookmarks_count')

        return queryset


def mountain_likes(request, mountain_pk):
    mountain = get_object_or_404(Mountain, pk=mountain_pk)
    user = request.user
    if user in mountain.likes.all():
        mountain.likes.remove(user)
        is_liked = False
    else:
        mountain.likes.add(user)
        is_liked = True

    return JsonResponse({'is_liked': is_liked, 'like_count':mountain.likes.count()})    


def bookmark(request, mountain_pk, course_pk):
    mountain = get_object_or_404(Mountain, pk=mountain_pk)
    course = get_object_or_404(Course, pk=course_pk)
    user = request.user
    if course in user.bookmarks.all():
        user.bookmarks.remove(course)
        is_bookmarked = False
    else:
        user.bookmarks.add(course)
        is_bookmarked = True
    context = {
        'is_bookmarked' : is_bookmarked,
    }
    return JsonResponse(context)


@login_required
def create_review(request, pk):
    mountain = Mountain.objects.get(pk=pk)

    if request.method == 'POST':
        form = ReviewCreationForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.mountain = mountain
            review.user = request.user
            review.save()
            form.save_m2m()

            return redirect('mountains:mountain_detail', pk)
    else:
        form = ReviewCreationForm()
    context = {
        'form': form,
        'pk': pk,
    }
    return render(request, 'mountains/mountain_detail.html', context)


@login_required
def review_likes(request, pk, review_pk):
    review = Review.objects.get(pk=review_pk)
    if request.user in review.like_users.all():
        review.like_users.remove(request.user)
    else:
        review.like_users.add(request.user)
    return redirect('mountains:mountain_detail', pk)


@login_required
def review_delete(request, pk, review_pk):
    review = Review.objects.get(pk=review_pk)
    if review.user == request.user:
        review.delete()
        return redirect('mountains:mountain_detail', pk)
    

@login_required
def review_update(request, pk, review_pk):
    review = Review.objects.get(pk=review_pk)
    if request.user == review.user:
        if request.method == 'POST':
            form = ReviewCreationForm(request.POST, request.FILES, instance=review)
            if form.is_valid():
                form.save()
                return redirect('mountains:mountain_detail', review.mountain.pk)
        else:
            form = ReviewCreationForm(instance=review)
    else:
        return JsonResponse({'message': '해당 리뷰를 작성한 유저가 아닙니다.'})
    context = {
        'form': form,
        'review': review,
    }
    return render(request, 'mountains/mountain_detail.html', context)