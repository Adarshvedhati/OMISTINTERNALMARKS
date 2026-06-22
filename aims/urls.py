# from django.urls import path

# from .views import (
#     # ── Template views (new) ──────────────────────────────────────────────
#     index,
#     marks_entry,
#     # ── REST API views (existing) ─────────────────────────────────────────
#     get_students,
#     save_marks,
#     download_excel,
#     marks_status,
#     get_marks,
# )

# # app_name enables {% url 'aims:index' %} and {% url 'aims:marks_entry' %}
# # in the templates.
# app_name = 'aims'

# urlpatterns = [

#     # ── Template pages ────────────────────────────────────────────────────
#     #   GET /          → index (selection form)
#     #   GET /marks/    → marks entry UI
#     path('',       index,       name='index'),
#     path('marks/', marks_entry, name='marks_entry'),

#     # ── REST API ──────────────────────────────────────────────────────────
#     #   Prefixed with api/ here so the root urls.py only needs:
#     #       path('', include('users.urls', namespace='aims'))
#     #   Final URLs become: /api/students/, /api/save-marks/, etc.
#     #   (matches apiBase: "/api" in marks_entry.html)
#     path('api/students/',        get_students,   name='api_students'),
#     path('api/save-marks/',      save_marks,     name='api_save_marks'),
#     path('api/download-excel/',  download_excel, name='api_download_excel'),
#     path('api/marks-status/',    marks_status,   name='api_marks_status'),
#     path('api/get-marks/',       get_marks,      name='api_get_marks'),
# ]
from django.urls import path
from . import views

app_name = "aims"

urlpatterns = [

    # ── Template pages ───────────────────────────────────────────────────────
    path("",             views.index,       name="index"),
    path("marks-entry/", views.marks_entry, name="marks_entry"),

    # ── REST API ─────────────────────────────────────────────────────────────

    # GET  /api/students/?college_code=&course=&semester=
    path("api/students/",       views.get_students,  name="get_students"),

    # POST /api/save-marks/
    path("api/save-marks/",     views.save_marks,    name="save_marks"),

    # GET  /api/get-marks/?student_id=&subject=&internal=
    path("api/get-marks/",      views.get_marks,     name="get_marks"),

    # GET  /api/download-excel/?faculty=&subject=&college=&course=&semester=
    #      Returns a combined sheet covering ALL internals for the class.
    #      MCA → 2 internals + average | MBA → 3 internals + sum
    path("api/download-excel/", views.download_excel, name="download_excel"),

    # GET  /api/marks-status/?college_code=&course=&semester=&subject=&internal=
    path("api/marks-status/",   views.marks_status,  name="marks_status"),
]