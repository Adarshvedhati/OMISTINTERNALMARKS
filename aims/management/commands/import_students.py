"""
Management command to import students from the 6 official roster Excel files.

Usage (run from project root):
    python manage.py import_students

Files expected in the project root:
    2144_mca_2_sem.xlsx   2174_mca_2_sem.xlsx
    2144_mca_4_sem.xlsx   2174_mca_4_sem.xlsx
    2144_mba_2_sem.xlsx   2174_mba_2_sem.xlsx

Each file has columns: S.No | college_code | HT NO | Name of the Student
Data rows start at row index 1 (row 0 is the header).

Note: The 2174 MBA file stores students with college_code=2177 — this is
intentional (different campus code) and preserved as-is in the database.
The frontend maps college selection "2174" → DB query for "2177" for MBA.
"""

import os
import pandas as pd
from django.core.management.base import BaseCommand
from aims.models import Student


ROSTER_FILES = [
    # (filename,           course, semester)
    ("2144_mca_2_sem.xlsx", "MCA",  2),
    ("2144_mca_4_sem.xlsx", "MCA",  4),
    ("2144_mba_2_sem.xlsx", "MBA",  2),
    ("2174_mca_2_sem.xlsx", "MCA",  2),
    ("2174_mca_4_sem.xlsx", "MCA",  4),
    ("2174_mba_2_sem.xlsx", "MBA",  2),
]


class Command(BaseCommand):
    help = "Import all student rosters from the 6 official Excel files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete ALL existing students before importing (use with caution)",
        )
        parser.add_argument(
            "--dir",
            type=str,
            default=".",
            help="Directory containing the roster Excel files (default: current directory)",
        )

    def handle(self, *args, **options):
        base_dir = options["dir"]

        if options["clear"]:
            count = Student.objects.count()
            Student.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {count} existing student records."))

        grand_total  = 0
        grand_new    = 0
        grand_skip   = 0
        grand_errors = 0

        for filename, course, semester in ROSTER_FILES:
            filepath = os.path.join(base_dir, filename)

            if not os.path.exists(filepath):
                self.stdout.write(self.style.ERROR(f"  FILE NOT FOUND: {filepath} — skipping"))
                continue

            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"  {filename}  ({course} Sem {semester})")
            self.stdout.write(f"{'='*60}")

            try:
                df = pd.read_excel(filepath, header=None)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Could not open file: {e}"))
                grand_errors += 1
                continue

            new_count   = 0
            skip_count  = 0
            error_count = 0

            # Row 0 = header; data starts at row 1
            for idx, row in df.iloc[1:].iterrows():
                try:
                    college_code = str(row[1]).strip()
                    roll_no      = str(row[2]).strip()
                    name         = str(row[3]).strip()
                except Exception:
                    error_count += 1
                    continue

                # Skip blank / header-repeat rows
                if (roll_no in ("nan", "", "HT NO") or
                        name in ("nan", "", "Name of the Student") or
                        college_code in ("nan", "", "college_code")):
                    continue

                # Validate: roll_no should look like a hall ticket (at least 6 chars)
                if len(roll_no) < 6:
                    continue

                try:
                    _, created = Student.objects.update_or_create(
                        roll_no=roll_no,
                        defaults={
                            "name":         name,
                            "college_code": college_code,
                            "course":       course,
                            "semester":     semester,
                        },
                    )
                    if created:
                        new_count += 1
                    else:
                        skip_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"    Row {idx}: {e}"))
                    error_count += 1

            self.stdout.write(self.style.SUCCESS(
                f"  ✓ Imported: {new_count}  |  Updated: {skip_count}  |  Errors: {error_count}"
            ))
            grand_total  += (new_count + skip_count)
            grand_new    += new_count
            grand_skip   += skip_count
            grand_errors += error_count

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(
            f"  DONE — New: {grand_new}  |  Updated: {grand_skip}  "
            f"|  Errors: {grand_errors}  |  Total in DB: {Student.objects.count()}"
        ))
