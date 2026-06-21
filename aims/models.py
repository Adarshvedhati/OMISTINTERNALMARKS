from django.db import models


from django.db import models


class Student(models.Model):

    roll_no = models.CharField(
        max_length=30,
        unique=True
    )

    name = models.CharField(
        max_length=200
    )

    college_code = models.CharField(
        max_length=10
    )

    course = models.CharField(
        max_length=20
    )

    semester = models.IntegerField()

    def __str__(self):
        return self.roll_no


class Marks(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    faculty_name = models.CharField(max_length=200)

    college_code = models.CharField(max_length=10)

    subject = models.CharField(max_length=200)

    internal = models.CharField(max_length=50)

    assignment_marks = models.IntegerField(
        null=True,
        blank=True
    )

    exam_marks = models.IntegerField(
        null=True,
        blank=True
    )

    marks = models.IntegerField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.student.roll_no}"