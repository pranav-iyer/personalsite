import csv
from datetime import datetime
from decimal import Decimal
from io import StringIO
import random
import re
from typing import Any, Dict
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import Http404
from django.forms.models import model_to_dict
from django.db.models import Sum
import base64
import calendar

from .forms import CSVDropForm, CSVDropSaveForm, TransactionReportForm
from .models import CATEGORIES_REVERSE, Transaction, CATEGORIES, MonthlyLimit

# Create your views here.
SOURCE_CATEGORIES = [
    ("Automotive", "Automotive"),
    ("Education", "Education"),
    ("Gasoline", "Gasoline"),
    ("Government Services", "Government Services"),
    ("Home Improvement", "Home Improvement"),
    ("Medical Services", "Medical Services"),
    ("Merchandise", "Merchandise"),
    ("Restaurants", "Restaurants"),
    ("Services", "Services"),
    ("Supermarkets", "Supermarkets"),
    ("Travel/Entertainment", "Travel/Entertainment"),
    ("Uncategorized", "Uncategorized"),
    ("Warehouse Clubs", "Warehouse Clubs"),
]


def home_view(request):
    if not request.GET.get("month") or not request.GET.get("year"):
        curr_month = datetime.now().month
        curr_year = datetime.now().year
        return redirect(
            reverse("budget:home") + f"?month={curr_month}&year={curr_year}"
        )
    month = int(request.GET["month"])
    year = int(request.GET["year"])
    first_of_month = datetime(year=year, month=month, day=1)
    context = {}
    context["month_name"] = first_of_month.strftime("%B")
    context["year_name"] = first_of_month.strftime("%Y")
    context["month"] = first_of_month.strftime("%m")
    context["last_day_of_month"] = str(calendar.monthrange(year, month)[1]).zfill(2)
    context.update(
        {
            "prev_month": month - 1 if month > 1 else 12,
            "prev_year": year if month > 1 else year - 1,
            "next_month": month + 1 if month < 12 else 1,
            "next_year": year if month < 12 else year + 1,
        }
    )
    context["transactions"] = [
        dupdate(
            model_to_dict(q),
            {
                "edited_category_label": q.get_edited_category_display(),
            },
        )
        for q in Transaction.objects.order_by("date")
    ]
    context["monthly_limits"] = []
    for q in MonthlyLimit.objects.all().order_by("edited_category"):
        spent = Transaction.objects.filter(
            date__month=month,
            date__year=year,
            edited_category=q.edited_category,
        ).aggregate(Sum("amount"))["amount__sum"]
        if spent is None:
            spent = 0
        progress = int(spent * 100 / q.monthly_limit)
        overshoot = min(progress - 100, 100)
        overshoot2 = min(progress - 200, 100)
        context["monthly_limits"].append(
            dupdate(
                model_to_dict(q),
                {
                    "spent": spent,
                    "over_budget": spent > q.monthly_limit,
                    "remaining": abs(q.monthly_limit - spent),
                    "progress": progress,
                    "overshoot": overshoot,
                    "overshoot2": overshoot2,
                    "edited_category_label": q.get_edited_category_display(),
                },
            )
        )
    context["edited_categories"] = CATEGORIES
    return render(request, "budget/home.html", context)


def discover_msgdrop(request):
    return render(request, "budget/discover_msgdrop.html")


def discover_view(request):
    if request.method == "POST":
        amount = Decimal(request.POST["amount"][1:])
        description = request.POST["description"]
        date = datetime.strptime(request.POST["date"], "%m/%d/%Y")
        category = request.POST["category"]
        Transaction.objects.create(
            source="Pranav Discover",
            amount=amount,
            date=date,
            description=description,
            category="Uncategorized",
            edited_category=category,
        )
        return redirect("budget:trans_report")
    else:
        if "msg" not in request.GET or request.GET["msg"] == "":
            return redirect("budget:discover_msgdrop")
        else:
            msg = base64.b64decode(request.GET["msg"]).decode("utf-8")
        # msg = "Discover Card: Transaction of $5.40 at PARKMOBILE-10 was made on August 20, 2022. See it at https://app.discover.com/ACTVT. Text STOP to quit."

        amount = ""
        description = ""
        date = ""
        error = ""

        amount_match = re.search(r"(\$\d+\.\d+)", msg)
        if amount_match is None:
            error = "Could not parse amount from message."
        else:
            amount = amount_match.group(1)

        desc_match = re.search(r"at (.*) was made on", msg)
        if desc_match is None:
            error = "Could not parse description from message."
        else:
            description = desc_match.group(1)

        date_match = re.search(r"was made on (.*)\. See it", msg)
        if date_match is None:
            error = "Could not parse date from message."
        else:
            try:
                date = datetime.strptime(date_match.group(1), "%B %d, %Y").strftime(
                    "%m/%d/%Y"
                )
            except ValueError:
                error = "Invalid date in message."

        # find potential duplicate
        dup_trans = Transaction.objects.filter(
            amount=Decimal(amount[1:]), date=datetime.strptime(date, "%m/%d/%Y")
        ).first()

        return render(
            request,
            "budget/discover.html",
            {
                "msg": msg,
                "amount": amount,
                "error": error,
                "description": description,
                "date": date,
                "category_choices": CATEGORIES,
                "dup_trans": dup_trans,
            },
        )


def dupdate(orig, new):
    orig.update(new)
    return orig


def transaction_report(request):
    context = {}
    context["report_data_json"] = [
        dupdate(
            model_to_dict(q),
            {
                "edited_category_label": q.get_edited_category_display(),
                "hidden": False,
            },
        )
        for q in Transaction.objects.order_by("date")
    ]
    context["column_info"] = [
        ("source", "Source", "string"),
        ("date", "Date", "date"),
        ("description", "Description", "string"),
        ("amount", "Amount", "money"),
        ("category", "Category", "string"),
        ("edited_category_label", "Edited Category", "string"),
    ]
    context["category_choices"] = SOURCE_CATEGORIES
    context["edited_category_choices"] = CATEGORIES
    return render(request, "budget/transaction_report.html", context)


def process_discover_reader(reader, source):
    results = []
    next(reader)  # skip header row
    for i, row in enumerate(reader):
        date = datetime.strptime(row[0], "%m/%d/%Y")
        amount = Decimal(row[3])
        dup_trans = Transaction.objects.filter(date=date, amount=amount).first()
        dup_desc = dup_trans.description if dup_trans is not None else ""
        dup_ed_cat = dup_trans.edited_category if dup_trans is not None else ""
        accepted = (amount > 0) and (dup_desc == "")
        results.append(
            {
                "index": i,
                "source": source,
                "date": date,
                "description": row[2],
                "amount": amount,
                "category": row[4],
                "edited_category": dup_ed_cat,
                "accepted": accepted,
                "dup_desc": dup_desc,
            }
        )
    return results


def process_capitalone_reader(reader, source):
    results = []
    next(reader)  # skip header row
    for i, row in enumerate(reader):
        date = datetime.strptime(row[1], "%m/%d/%y")
        amount = -Decimal(row[2])
        dup_trans = Transaction.objects.filter(date=date, amount=amount).first()
        dup_desc = dup_trans.description if dup_trans is not None else ""
        dup_ed_cat = dup_trans.edited_category if dup_trans is not None else ""
        accepted = (amount > 0) and (dup_desc == "")
        results.append(
            {
                "index": i,
                "source": source,
                "date": date,
                "description": row[4],
                "amount": amount,
                "category": "Uncategorized",
                "edited_category": dup_ed_cat,
                "accepted": accepted,
                "dup_desc": dup_desc,
            }
        )
    return results


def process_already_processed(reader):
    results = []
    for i, row in enumerate(reader):
        source = row[0]
        date = datetime.strptime(row[1], "%m/%d/%Y")
        description = row[2]
        amount = Decimal(row[3][1:].replace(",", ""))
        category = row[4]
        edited_category = CATEGORIES_REVERSE[row[5]]
        dup_trans = Transaction.objects.filter(date=date, amount=amount).first()
        dup_desc = dup_trans.description if dup_trans is not None else ""
        accepted = (amount > 0) and (dup_desc == "")
        results.append(
            {
                "index": i,
                "source": source,
                "date": date,
                "description": description,
                "amount": amount,
                "category": category,
                "edited_category": edited_category,
                "accepted": accepted,
                "dup_desc": dup_desc,
            }
        )
    return results


def csvdrop(request):
    if request.method == "POST":
        form = CSVDropForm(request.POST, request.FILES)
        if form.is_valid():
            text_content = form.cleaned_data["csv_file"].read().decode("utf-8")
            reader = csv.reader(StringIO(text_content), delimiter=",")
            if form.cleaned_data["source"] == "Pranav Discover":
                results = process_discover_reader(reader, "Pranav Discover")
            elif form.cleaned_data["source"] == "Katey Discover":
                results = process_discover_reader(reader, "Katey Discover")
            elif form.cleaned_data["source"] == "Already Processed":
                results = process_already_processed(reader)
            elif form.cleaned_data["source"] == "Katey CapitalOne":
                results = process_capitalone_reader(reader, "Katey CapitalOne")
            else:
                results = None

            return render(
                request,
                "budget/csvdrop_qc.html",
                {"results": results, "category_choices": CATEGORIES},
            )
    else:
        form = CSVDropForm()
    return render(request, "budget/csvdrop.html", {"form": form})


def csvdrop_save(request):
    if request.method == "POST":
        form = CSVDropSaveForm(request.POST)
        if form.is_valid():
            for row in form.cleaned_data["transactions"]:
                if row["accepted"]:
                    Transaction.objects.create(
                        source=row["source"],
                        amount=row["amount"],
                        date=row["date"][:10],
                        description=row["description"],
                        category=row["category"],
                        edited_category=row["edited_category"],
                    )
                else:
                    dup_trans = Transaction.objects.filter(
                        amount=row["amount"], description=row["dup_desc"]
                    ).first()
                    if dup_trans is not None and dup_trans.category == "Uncategorized":
                        dup_trans.category = row["category"]
                        dup_trans.save()
        return redirect("budget:trans_report")
    else:
        raise Http404()
