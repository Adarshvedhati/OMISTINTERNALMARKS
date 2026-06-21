from rest_framework import serializers
from .models import Student, Marks


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Student
        fields = ["id", "roll_no", "name", "college_code", "course", "semester"]


class MarksSerializer(serializers.ModelSerializer):
    student_roll_no = serializers.CharField(source="student.roll_no", read_only=True)
    student_name    = serializers.CharField(source="student.name",    read_only=True)

    class Meta:
        model  = Marks
        fields = [
            "id", "student", "student_roll_no", "student_name",
            "faculty_name", "college_code", "subject", "internal",
            "exam_marks", "assignment_marks", "marks", "created_at",
        ]
