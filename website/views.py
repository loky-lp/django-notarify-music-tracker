import requests
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError, JsonResponse, \
    HttpResponseNotFound
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .models import Artist, Album, Song, UserTrack


@login_required(login_url="/login")
def index(request):
    if Artist.objects.all().count() == 0:
        context = {
            'should_initialize': True,
            'total_saves': 0,
            'artists': [],
        }
        return render(request, "website/index.html", context)

    artists = Artist.objects.prefetch_related('album_set')
    context = {
        'should_initialize': False,
        'total_saves': UserTrack.objects.filter(user_id=request.user).count(),
        'artists': [
            {
                'id': artist.id,
                'name': artist.name,
                'albums': [
                    {
                        'title': album.title,
                        'img_url': album.img_url
                    } for album in artist.album_set.all()
                ],
            }
            for artist in artists
        ],
    }

    return render(request, "website/index.html", context)


@login_required(login_url="/login")
def artist_details(request, artist_id):
    try:
        artist = Artist.objects.prefetch_related(
            Prefetch(
                'album_set',
                queryset=Album.objects.prefetch_related(
                    Prefetch(
                        'song_set',
                        queryset=Song.objects.prefetch_related(
                            Prefetch(
                                'usertrack_set',
                                queryset=UserTrack.objects.filter(user_id=request.user).all()
                            )
                        )
                    )
                )
            )
        ).get(id=artist_id)
    except Artist.DoesNotExist:
        return HttpResponseNotFound()

    context = {
        'name': artist.name,
        'albums': [
            {
                'title': album.title,
                'img_url': album.img_url,
                'songs': [
                    {
                        'id': song.id,
                        'title': song.title,
                        # 'is_saved': UserTrack.objects.filter(song_id=song, user_id=request.user).count() > 0
                        'is_saved': song.usertrack_set.filter(user_id=request.user).count() > 0
                    } for song in album.song_set.all()
                ]
            } for album in artist.album_set.all()
        ],
    }

    return render(request, "website/artist.html", context)


@csrf_exempt
@login_required(login_url="/login")
def song_action(request, song_id):
    print(request.method)

    match request.method:
        case "POST":
            user = request.user
            try:
                song = Song.objects.get(id=song_id)
            except Song.DoesNotExist:
                return HttpResponseNotFound()

            if UserTrack.objects.filter(song_id=song, user_id=user).count() is 0:
                UserTrack.objects.create(song_id=song, user_id=user)

            return JsonResponse({"success": True})
        case "DELETE":
            user = request.user
            try:
                song = Song.objects.get(id=song_id)
            except Song.DoesNotExist:
                return HttpResponseNotFound()

            track = UserTrack.objects.filter(song_id=song, user_id=user)
            if track.count() > 0:
                track.delete()

            return JsonResponse({"success": True})
        case _:
            return HttpResponseNotAllowed(HttpResponse("Method not valid"))


@csrf_exempt
@login_required(login_url="/login")
def populate_db(request):
    if Artist.objects.all().count() > 0:
        return redirect("website:index")

    # Populate db
    hardcoded_data = [
        {  # Pink Floyd
            'artist': "83d91898-7763-47d7-b03b-b92132375c47",
            'albums': [
                # The Dark Side of the Moon
                {'cover': "f5093c06-23e3-404f-aeaa-40f72885ee3a", 'data': "b84ee12a-09ef-421b-82de-0441a926375b"},
                # The Wall
                {'cover': "f2026101-945b-3d05-9ef4-aa718fc3feef", 'data': "93c4f215-15ae-34a2-981a-9a5fbd700004"},
                # Wish You Were Here
                {'cover': "1a272023-10d3-38ee-bab3-317b55fcc21d", 'data': "f4a8aa35-da90-33d8-9307-c630d38a2bed"},
                # The Division Bell
                {'cover': "90878b63-f639-3c8b-aefb-190bdf3d1790", 'data': "f8297e31-e3c7-427a-aad5-459647382b76"},
            ]
        },
        {  # AC/DC
            'artist': "66c662b6-6e2f-4930-8610-912e24c63ed1",
            'albums': [
                # Highway to Hell
                {'cover': "f85647ec-a69b-3b0a-ad04-bb6076c4dcf1", 'data': "8866e226-7cd6-414e-b7d2-6ae0b0df6715"},
                # Back in Black
                {'cover': "d3bc1a64-7561-3787-b680-0003aa50f8f1", 'data': "f7c680af-5b09-3fea-be84-5e00a7da56a0"},
                # The Razors Edge
                {'cover': "03759365-2f74-3f12-b884-280d3aa17f0e", 'data': "ecc5dddd-268a-4bcf-aa0b-affb3b6c8ffc"},
                # Black Ice
                {'cover': "afca53c1-c5b3-3f91-8590-281b0aa12722", 'data': "7d73370a-546d-4037-a40f-72669b6772e4"},
            ]
        },
        {  # Daft Punk
            'artist': "056e4f3e-d505-4dad-8ec1-d04f521cbb56",
            'albums': [
                # Homework
                {'cover': "00054665-89fa-33d5-a8f0-1728ea8c32c3", 'data': "770b9b80-10e1-4297-b1fd-46ad0dbb0305"},
                # Discovery
                {'cover': "48117b90-a16e-34ca-a514-19c702df1158", 'data': "bd3bb36e-16c8-438f-850e-dfbf4d1478f0"},
                # Human After All
                {'cover': "f9e8042a-674e-3f01-80ec-7f0ab1c537df", 'data': "7f293aa6-8c19-4695-80bb-63ac40a0f2b5"},
                # Random Access Memories
                {'cover': "aa997ea0-2936-40bd-884d-3af8a0e064dc", 'data': "bbfc83ad-826f-4957-893d-a808105c828b"},
            ]
        },
    ]

    # I guess this implementation is suboptimal, not knowing how python handles asynchronous tasks there could bee
    # room for improvement.
    # Ideally (if the API won't rate limit us) each request should be made in parallel.
    for datum in hardcoded_data:
        r = requests.get(f"https://musicbrainz.org/ws/2/artist/{datum['artist']}?fmt=json")
        if r.status_code != 200:
            return HttpResponseServerError('Server error')

        api_artist = r.json()
        Artist.objects.create(mdbId=api_artist['id'], name=api_artist['name'])

        for album_data in datum['albums']:
            # Get and save album data
            r = requests.get(f"https://musicbrainz.org/ws/2/release/{album_data['data']}?fmt=json&inc=recordings")
            if r.status_code != 200:
                return HttpResponseServerError('Server error')

            api_album = r.json()
            album = Album(
                mdbId=api_album['id'],
                artist=Artist.objects.get(mdbId=api_artist['id']),
                title=api_album['title'],
                pub_date=api_album['date'],
            )

            # Get and save cover data
            r = requests.get(f"https://coverartarchive.org/release-group/{album_data['cover']}", allow_redirects=True)
            if r.status_code != 200:
                return HttpResponseServerError('Server error')

            api_cover = r.json()

            for image in api_cover['images']:
                if not image['approved']:
                    continue

                album.img_url = image['image']
                break

            album.save()

            # Save album tracks
            for api_song in api_album['media'][0]['tracks']:
                Song.objects.create(
                    title=api_song['title'],
                    mdbId=api_song['id'],
                    album=album,
                )

    return redirect("website:index")


@csrf_exempt  # DISABLED ONLY FOR DEMONSTRATION PURPOSES, in production environments the CSRF check MUST be activated
def login(request):
    if request.user.is_authenticated:
        return redirect("website:index")

    match request.method:
        case "GET":
            return render(request, "website/login.html")
        case "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                django_login(request, user)
                return redirect("website:index")
            else:
                context = {'error': "Credenziali non valide"}
                return render(request, "website/login.html", context)
        case _:
            return HttpResponseNotAllowed(HttpResponse("Method not valid"))


@csrf_exempt
def signup(request):
    if request.user.is_authenticated:
        return redirect("website:index")

    return render(request, 'website/signup.html')


@csrf_exempt
def logout(request):
    if not request.user.is_authenticated:
        return redirect("website:index")

    match request.method:
        case "POST":
            django_logout(request)
            return redirect("website:index")
        case _:
            return HttpResponseNotAllowed(HttpResponse("Method not valid"))
