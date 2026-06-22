# from django.http import HttpResponse
# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.views.decorators.csrf import ensure_csrf_cookie

# import pandas as pd

# from rest_framework.decorators import api_view
# from rest_framework.response import Response

# from .models import Student, Marks
# from .serializers import StudentSerializer


# # ── Template views ──────────────────────────────────────────────────────────

# @ensure_csrf_cookie          # ensures csrftoken cookie is set for JS fetch()
# def index(request):
#     """Selection page — renders aims/index.html (converted from App.jsx)"""
#     return render(request, 'index.html')


# @ensure_csrf_cookie
# def marks_entry(request):
#     """Marks entry page — renders aims/marks_entry.html (converted from MarksEntry.jsx)
#     Reads all form values from GET params sent by the index form.
#     """
#     context = {
#         'faculty_name': request.GET.get('faculty_name', '').strip(),
#         'college_code': request.GET.get('college_code', '').strip(),
#         'course':       request.GET.get('course',       '').strip(),
#         'semester':     request.GET.get('semester',     '0').strip(),
#         'subject':      request.GET.get('subject',      '').strip(),
#         'internal':     request.GET.get('internal',     '').strip(),
#     }
#     # Guard: bounce back if no college was selected
#     if not context['college_code']:
#         return redirect(reverse('aims:index'))
#     return render(request, 'marks_entry.html', context)


# # ── REST API views (unchanged) ──────────────────────────────────────────────

# # ---------------------------------------------------------------------------
# # GET /api/students/?college_code=2144&course=MCA&semester=2
# # ---------------------------------------------------------------------------
# @api_view(["GET"])
# def get_students(request):
#     college_code = request.GET.get("college_code", "").strip()
#     course       = request.GET.get("course", "").strip().upper()
#     semester     = request.GET.get("semester", "").strip()

#     if not college_code or not course or not semester:
#         return Response({"error": "college_code, course and semester are required."}, status=400)

#     try:
#         semester = int(semester)
#     except ValueError:
#         return Response({"error": "semester must be an integer."}, status=400)

#     # 2174 campus MBA students are stored with college_code=2177 in the data
#     if college_code == "2174" and course == "MBA":
#         students = Student.objects.filter(
#             college_code="2177", course=course, semester=semester
#         )
#     else:
#         students = Student.objects.filter(
#             college_code=college_code, course=course, semester=semester
#         )

#     serializer = StudentSerializer(students, many=True)
#     return Response(serializer.data)


# # ---------------------------------------------------------------------------
# # POST /api/save-marks/
# # ---------------------------------------------------------------------------
# @api_view(["POST"])
# def save_marks(request):
#     data = request.data

#     student_id   = data.get("student_id")
#     faculty_name = data.get("faculty_name", "").strip()
#     college_code = data.get("college_code", "").strip()
#     subject      = data.get("subject",      "").strip()
#     internal     = data.get("internal",     "").strip()
#     course       = data.get("course",       "").strip().upper()

#     if not all([student_id, faculty_name, college_code, subject, internal, course]):
#         return Response({"error": "Missing required fields."}, status=400)

#     try:
#         student = Student.objects.get(id=student_id)
#     except Student.DoesNotExist:
#         return Response({"error": "Student not found."}, status=404)

#     # MCA: descriptive (0-20) + assignment (0-10); marks = total
#     # MBA: single marks field (0-20)
#     if course == "MCA":
#         try:
#             descriptive = int(data.get("descriptive_marks", 0) or 0)
#             assignment  = int(data.get("assignment_marks",  0) or 0)
#         except (ValueError, TypeError):
#             return Response({"error": "descriptive_marks and assignment_marks must be integers."}, status=400)

#         if not (10 <= descriptive <= 20):
#             return Response({"error": "descriptive_marks must be between 10 and 20."}, status=400)
#         if not (5 <= assignment <= 10):
#             return Response({"error": "assignment_marks must be between 5 and 10."}, status=400)

#         total = descriptive + assignment

#         mark_obj, created = Marks.objects.update_or_create(
#             student=student,
#             subject=subject,
#             internal=internal,
#             defaults={
#                 "faculty_name":    faculty_name,
#                 "college_code":    college_code,
#                 "exam_marks":      descriptive,   # exam_marks stores descriptive
#                 "assignment_marks": assignment,
#                 "marks":           total,
#             }
#         )
#     else:
#         # MBA
#         try:
#             mba_marks = float(data.get("marks", 0) or 0)
#         except (ValueError, TypeError):
#             return Response({"error": "marks must be a number."}, status=400)

#         if not (0 <= mba_marks <= 10):
#             return Response({"error": "marks must be between 0 and 10."}, status=400)

#         mark_obj, created = Marks.objects.update_or_create(
#             student=student,
#             subject=subject,
#             internal=internal,
#             defaults={
#                 "faculty_name": faculty_name,
#                 "college_code": college_code,
#                 "marks":        mba_marks,
#             }
#         )

#     return Response({"success": True, "created": created})


# # ---------------------------------------------------------------------------
# # GET /api/get-marks/?student_id=X&subject=Y&internal=Z
# # ---------------------------------------------------------------------------
# @api_view(["GET"])
# def get_marks(request):
#     student_id = request.GET.get("student_id")
#     subject    = request.GET.get("subject")
#     internal   = request.GET.get("internal")

#     try:
#         mark = Marks.objects.get(
#             student_id=student_id,
#             subject=subject,
#             internal=internal,
#         )
#         return Response({
#             "found":            True,
#             "exam_marks":       mark.exam_marks,        # descriptive for MCA
#             "assignment_marks": mark.assignment_marks,
#             "marks":            mark.marks,
#         })
#     except Marks.DoesNotExist:
#         return Response({"found": False})


# # ---------------------------------------------------------------------------
# # GET /api/download-excel/?faculty=X&subject=Y&college=Z&course=MCA&semester=2&internal=Internal+1
# # ---------------------------------------------------------------------------
# @api_view(["GET"])
# def download_excel(request):
#     faculty  = request.GET.get("faculty",  "").strip()
#     subject  = request.GET.get("subject",  "").strip()
#     college  = request.GET.get("college",  "").strip()
#     course   = request.GET.get("course",   "").strip().upper()
#     semester = request.GET.get("semester", "").strip()
#     internal = request.GET.get("internal", "").strip()

#     filters = dict(faculty_name=faculty, subject=subject, college_code=college)
#     if internal:
#         filters["internal"] = internal

#     records = Marks.objects.filter(**filters).select_related("student")

#     data = []
#     for item in records:
#         row = {
#             "Hall Ticket No": item.student.roll_no,
#             "Student Name":   item.student.name,
#             "College":        item.college_code,
#             "Course":         item.student.course,
#             "Semester":       item.student.semester,
#             "Subject":        item.subject,
#             "Internal":       item.internal,
#             "Faculty":        item.faculty_name,
#         }
#         if item.student.course == "MCA":
#             row["Descriptive Marks (10-20)"] = item.exam_marks
#             row["Assignment Marks (5-10)"]  = item.assignment_marks
#             row["Total Marks (15-30)"]       = item.marks
#         else:
#             row["Marks (10-20)"] = item.marks
#         data.append(row)

#     df = pd.DataFrame(data)

#     response = HttpResponse(
#         content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )
#     safe_internal = internal.replace(" ", "_") if internal else "all"
#     filename = f"{faculty}_{subject}_{college}_{safe_internal}.xlsx"
#     response["Content-Disposition"] = f'attachment; filename="{filename}"'
#     df.to_excel(response, index=False)
#     return response


# # ---------------------------------------------------------------------------
# # GET /api/marks-status/?college_code=2144&course=MCA&semester=2&subject=DBMS&internal=Internal+1
# # ---------------------------------------------------------------------------
# @api_view(["GET"])
# def marks_status(request):
#     college  = request.GET.get("college_code", "").strip()
#     course   = request.GET.get("course",       "").strip().upper()
#     semester = request.GET.get("semester",     "").strip()
#     subject  = request.GET.get("subject",      "").strip()
#     internal = request.GET.get("internal",     "").strip()

#     college_filter = "2177" if (college == "2174" and course == "MBA") else college

#     try:
#         sem = int(semester)
#     except ValueError:
#         return Response({"error": "semester must be an integer."}, status=400)

#     student_ids = Student.objects.filter(
#         college_code=college_filter, course=course, semester=sem
#     ).values_list("id", flat=True)

#     existing = Marks.objects.filter(
#         student_id__in=student_ids,
#         subject=subject,
#         internal=internal,
#     ).values("student_id", "exam_marks", "assignment_marks", "marks")

#     existing_map = {m["student_id"]: m for m in existing}

#     return Response({
#         "total":    len(student_ids),
#         "saved":    len(existing_map),
#         "existing": existing_map,
#     })
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

import pandas as pd

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Student, Marks
from .serializers import StudentSerializer
from .utils import (
    INTERNALS_BY_COURSE,
    build_marks_map,
    get_college_filter,
)


# ── Template views ───────────────────────────────────────────────────────────

@ensure_csrf_cookie
def index(request):
    """Selection page — renders aims/index.html."""
    return render(request, 'index.html')


@ensure_csrf_cookie
def marks_entry(request):
    """
    Marks entry page — reads all form values from GET params
    sent by the index form.
    """
    context = {
        'faculty_name': request.GET.get('faculty_name', '').strip(),
        'college_code': request.GET.get('college_code', '').strip(),
        'course':       request.GET.get('course',       '').strip(),
        'semester':     request.GET.get('semester',     '0').strip(),
        'subject':      request.GET.get('subject',      '').strip(),
        'internal':     request.GET.get('internal',     '').strip(),
    }
    if not context['college_code']:
        return redirect(reverse('aims:index'))
    return render(request, 'marks_entry.html', context)


# ── REST API views ───────────────────────────────────────────────────────────

# ---------------------------------------------------------------------------
# GET /api/students/?college_code=2144&course=MCA&semester=2
# ---------------------------------------------------------------------------
@api_view(["GET"])
def get_students(request):
    college_code = request.GET.get("college_code", "").strip()
    course       = request.GET.get("course",       "").strip().upper()
    semester     = request.GET.get("semester",     "").strip()

    if not college_code or not course or not semester:
        return Response(
            {"error": "college_code, course and semester are required."},
            status=400,
        )

    try:
        semester = int(semester)
    except ValueError:
        return Response({"error": "semester must be an integer."}, status=400)

    college_filter = get_college_filter(college_code, course)

    students = Student.objects.filter(
        college_code=college_filter, course=course, semester=semester
    )
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)


# ---------------------------------------------------------------------------
# POST /api/save-marks/
# ---------------------------------------------------------------------------
@api_view(["POST"])
def save_marks(request):
    data = request.data

    student_id   = data.get("student_id")
    faculty_name = data.get("faculty_name", "").strip()
    college_code = data.get("college_code", "").strip()
    subject      = data.get("subject",      "").strip()
    internal     = data.get("internal",     "").strip()
    course       = data.get("course",       "").strip().upper()

    if not all([student_id, faculty_name, college_code, subject, internal, course]):
        return Response({"error": "Missing required fields."}, status=400)

    # Validate internal value against course-specific list
    allowed_internals = INTERNALS_BY_COURSE.get(course, [])
    if internal not in allowed_internals:
        return Response(
            {"error": f"Invalid internal '{internal}' for course {course}. "
                      f"Allowed: {allowed_internals}"},
            status=400,
        )

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({"error": "Student not found."}, status=404)

    if course == "MCA":
        # MCA: descriptive (10-20) + assignment (5-10); marks = total
        try:
            descriptive = int(data.get("descriptive_marks", 0) or 0)
            assignment  = int(data.get("assignment_marks",  0) or 0)
        except (ValueError, TypeError):
            return Response(
                {"error": "descriptive_marks and assignment_marks must be integers."},
                status=400,
            )

        if not (10 <= descriptive <= 20):
            return Response(
                {"error": "descriptive_marks must be between 10 and 20."},
                status=400,
            )
        if not (5 <= assignment <= 10):
            return Response(
                {"error": "assignment_marks must be between 5 and 10."},
                status=400,
            )

        total = descriptive + assignment

        mark_obj, created = Marks.objects.update_or_create(
            student=student,
            subject=subject,
            internal=internal,
            defaults={
                "faculty_name":     faculty_name,
                "college_code":     college_code,
                "exam_marks":       descriptive,   # descriptive stored in exam_marks
                "assignment_marks": assignment,
                "marks":            total,
            },
        )

    else:
        # MBA: single marks field per internal (0-10)
        try:
            mba_marks = float(data.get("marks", 0) or 0)
        except (ValueError, TypeError):
            return Response({"error": "marks must be a number."}, status=400)

        if not (0 <= mba_marks <= 10):
            return Response(
                {"error": "marks must be between 0 and 10."},
                status=400,
            )

        mark_obj, created = Marks.objects.update_or_create(
            student=student,
            subject=subject,
            internal=internal,
            defaults={
                "faculty_name": faculty_name,
                "college_code": college_code,
                "marks":        mba_marks,
            },
        )

    return Response({"success": True, "created": created})


# ---------------------------------------------------------------------------
# GET /api/get-marks/?student_id=X&subject=Y&internal=Z
# ---------------------------------------------------------------------------
@api_view(["GET"])
def get_marks(request):
    student_id = request.GET.get("student_id")
    subject    = request.GET.get("subject")
    internal   = request.GET.get("internal")

    try:
        mark = Marks.objects.get(
            student_id=student_id,
            subject=subject,
            internal=internal,
        )
        return Response({
            "found":            True,
            "exam_marks":       mark.exam_marks,        # descriptive for MCA
            "assignment_marks": mark.assignment_marks,
            "marks":            mark.marks,
        })
    except Marks.DoesNotExist:
        return Response({"found": False})


# ---------------------------------------------------------------------------
# GET /api/download-excel/
#     ?faculty=X&subject=Y&college=Z&course=MCA&semester=2
#
# Downloads a combined sheet for ALL internals (MCA: 2, MBA: 3).
# Students without marks entered are included with 0s.
#
# MCA columns : Roll No | Name |
#               Int-1 Descriptive | Int-1 Assignment | Int-1 Total |
#               Int-2 Descriptive | Int-2 Assignment | Int-2 Total |
#               Average
#
# MBA columns : Roll No | Name |
#               Internal 1 Marks | Internal 2 Marks | Internal 3 Marks |
#               Sum
# ---------------------------------------------------------------------------
@api_view(["GET"])
def download_excel(request):
    faculty  = request.GET.get("faculty",  "").strip()
    subject  = request.GET.get("subject",  "").strip()
    college  = request.GET.get("college",  "").strip()
    course   = request.GET.get("course",   "").strip().upper()
    semester = request.GET.get("semester", "").strip()

    if not all([subject, college, course, semester]):
        return Response(
            {"error": "subject, college, course and semester are required."},
            status=400,
        )

    college_filter = get_college_filter(college, course)

    try:
        sem = int(semester)
    except ValueError:
        return Response({"error": "semester must be an integer."}, status=400)

    internals = INTERNALS_BY_COURSE.get(course)
    if not internals:
        return Response({"error": f"Unknown course '{course}'."}, status=400)

    # ── 1. All students in this class, ordered by roll number ────────────────
    students = Student.objects.filter(
        college_code=college_filter, course=course, semester=sem
    ).order_by("roll_no")

    # ── 2. Fetch marks for ALL internals in a single query ───────────────────
    marks_qs = Marks.objects.filter(
        student__in=students,
        subject=subject,
        internal__in=internals,
    ).select_related("student")

    # ── 3. Build lookup {student_id: {"Internal 1": obj, ...}} ───────────────
    marks_map = build_marks_map(marks_qs)

    # ── 4. Build rows — every student appears; missing marks default to 0 ────
    rows = []
    for stu in students:
        stu_marks = marks_map.get(stu.id, {})
        row = {"Roll No": stu.roll_no, "Name": stu.name}

        if course == "MCA":
            m1 = stu_marks.get("Internal 1")
            m2 = stu_marks.get("Internal 2")

            i1_desc  = m1.exam_marks       if m1 else 0
            i1_asn   = m1.assignment_marks if m1 else 0
            i1_total = m1.marks            if m1 else 0

            i2_desc  = m2.exam_marks       if m2 else 0
            i2_asn   = m2.assignment_marks if m2 else 0
            i2_total = m2.marks            if m2 else 0

            # Average of both internal totals (zeros counted for missing entries)
            average = round((i1_total + i2_total) / 2, 2)

            row.update({
                "Int-1 Descriptive (10-20)": i1_desc,
                "Int-1 Assignment (5-10)":   i1_asn,
                "Int-1 Total":               i1_total,
                "Int-2 Descriptive (10-20)": i2_desc,
                "Int-2 Assignment (5-10)":   i2_asn,
                "Int-2 Total":               i2_total,
                "Average":                   average,
            })

        else:  # MBA — 3 internals, show sum
            m1 = stu_marks.get("Internal 1")
            m2 = stu_marks.get("Internal 2")
            m3 = stu_marks.get("Internal 3")

            i1 = m1.marks if m1 else 0
            i2 = m2.marks if m2 else 0
            i3 = m3.marks if m3 else 0

            row.update({
                "Internal 1 Marks": i1,
                "Internal 2 Marks": i2,
                "Internal 3 Marks": i3,
                "Sum":              round(i1 + i2 + i3, 2),
            })

        rows.append(row)

    # ── 5. Stream as .xlsx ───────────────────────────────────────────────────
    df = pd.DataFrame(rows)
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"{course}_{subject}_{college}_sem{sem}_all_internals.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    df.to_excel(response, index=False)
    return response


# ---------------------------------------------------------------------------
# GET /api/marks-status/
#     ?college_code=2144&course=MCA&semester=2&subject=DBMS&internal=Internal+1
# ---------------------------------------------------------------------------
@api_view(["GET"])
def marks_status(request):
    college  = request.GET.get("college_code", "").strip()
    course   = request.GET.get("course",       "").strip().upper()
    semester = request.GET.get("semester",     "").strip()
    subject  = request.GET.get("subject",      "").strip()
    internal = request.GET.get("internal",     "").strip()

    college_filter = get_college_filter(college, course)

    try:
        sem = int(semester)
    except ValueError:
        return Response({"error": "semester must be an integer."}, status=400)

    student_ids = Student.objects.filter(
        college_code=college_filter, course=course, semester=sem
    ).values_list("id", flat=True)

    existing = Marks.objects.filter(
        student_id__in=student_ids,
        subject=subject,
        internal=internal,
    ).values("student_id", "exam_marks", "assignment_marks", "marks")

    existing_map = {m["student_id"]: m for m in existing}

    return Response({
        "total":    len(student_ids),
        "saved":    len(existing_map),
        "existing": existing_map,
    })