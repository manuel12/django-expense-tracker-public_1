from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse, request
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum

from .forms import BudgetForm, ExpenseForm
from .models import Budget, Expense
from expenses import utils 

# Create your views here.

@login_required
def homepage(request):
    Expense.objects.add_testuser_expenses(request)

    template = 'homepage.html'
    user_expenses = Expense.objects.filter(owner=request.user).order_by('-date')
  
    total_expense_amount = Expense.objects.get_total_expenses(owner=request.user)
    budget = Expense.objects.get_budget(owner=request.user)

    page = request.GET.get('page', 1)
    paginator = Paginator(user_expenses, 15)


    try:   
        expenses = paginator.page(page)
    except PageNotAnInteger:
        expenses = paginator.page(1)
    except EmptyPage:
        expenses = paginator.page(paginator.num_pages)

    pagination_range_down = expenses.number - 5
    pagination_range_up = expenses.number + 5

    context = { 
      'expenses': expenses,
      'total_expense_amount': total_expense_amount,
      'budget': budget,
      'num_expenses': len(user_expenses),
      'num_pages': paginator.num_pages,
      'pagination_range_down': pagination_range_down,
      'pagination_range_up': pagination_range_up
    }

    if budget:
      current_month_expenses = Expense.objects.get_monthly_expense_sum(owner=request.user)
      expenses_vs_budget_percentage_diff = (current_month_expenses / budget * 100) if budget else 0
      over_budget = current_month_expenses - budget

      context['current_month_expenses'] = current_month_expenses
      context['expenses_vs_budget_percentage_diff'] = expenses_vs_budget_percentage_diff
      context['over_budget'] = over_budget

    return render(request, template, context)

@login_required
def charts(request):
    template = 'charts.html'
    expenses = Expense.objects.filter(owner=request.user)
    budget = Expense.objects.get_budget(request.user)
    statistics = Expense.objects.get_statistics(request.user)

    context = {
      'expenses': expenses,
      'budget': budget, 
      'statistics': statistics
    }
    return render(request, template, context)


@login_required
def add_expense(request):
    template = 'add_expense.html'

    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = ExpenseForm()
    else:
        # POST data submitted; process data.
        form = ExpenseForm(request.POST)
        if form.is_valid():
            new_expense = form.save(commit=False)
            new_expense.owner = request.user
            new_expense.save()
            return redirect('expenses:home')

    context = locals()
    return render(request, template, context)


@login_required
def view_expense(request, pk):
    template = 'view_expense.html'
    expense = get_object_or_404(Expense, pk=pk)
    context = locals()

    return render(request, template, context)


@login_required
def update_expense(request, pk):
    template = 'update_expense.html'
    expense = get_object_or_404(Expense, pk=pk)

    if request.method != 'POST':
        form = ExpenseForm(instance=expense)

    else:
        form = ExpenseForm(instance=expense, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('expenses:home')

    context = locals()
    return render(request, template, context)


@login_required
def delete_expense(request, pk):
    template = 'delete_expense.html'
    expense = get_object_or_404(Expense, pk=pk)

    if request.method == 'POST':
        expense.delete()
        return redirect('expenses:home')

    return render(request, template, {})


@login_required
def add_budget(request):
    template = 'add_budget.html'

    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = BudgetForm()
    else:
        # POST data submitted; process data.
        form = BudgetForm(request.POST)
        if form.is_valid():
            new_budget = form.save(commit=False)
            new_budget.owner = request.user
            new_budget.save()
            return redirect('expenses:home')

    context = locals()
    return render(request, template, context)


@login_required
def update_budget(request):
    template = 'update_budget.html'
    budget = get_object_or_404(Budget, owner=request.user)

    if request.method != 'POST':
        form = BudgetForm(instance=budget)

    else:
        form = BudgetForm(instance=budget, data=request.POST)
        if form.is_valid():
            updated_budget = form.save(commit=False)
            updated_budget.owner = request.user
            updated_budget.save()
            return redirect('expenses:home')

    context = locals()
    return render(request, template, context)


@login_required
def delete_budget(request):
    template = 'delete_budget.html'
    budget = get_object_or_404(Budget, owner=request.user)

    if request.method == 'POST':
        budget.delete()
        return redirect('expenses:home')

    return render(request, template, {})


@login_required
def view_404(request, exception):
    template = 'errors/404.html'
    return render(request, template, {})


@login_required
def view_500(request):
    template = 'errors/500.html'
    return render(request, template, {})


@login_required
def line_chart_data(request):
    user_expenses = Expense.objects.filter(owner=request.user)

    page = request.GET.get('page', 1)
    paginator = Paginator(user_expenses, 15)

    try:   
        expenses = paginator.page(page)
    except PageNotAnInteger:
        expenses = paginator.page(1)
    except EmptyPage:
        expenses = paginator.page(paginator.num_pages)

    dates =  [exp.date for exp in expenses]
    dates = [utils.reformat_date(date, "%d' %b") for date in dates]
    dates.reverse()

    amounts = [round(float(exp.amount), 2) for exp in expenses]
    amounts.reverse()

    chart_data = {}

    for i in range(len(dates)):
      if dates[i] not in chart_data:
          chart_data[dates[i]] = amounts[i]
      else:
          chart_data[dates[i]] += amounts[i]
    return JsonResponse(chart_data)
    

@login_required
def total_expenses_pie_chart_data(request):
    user_expenses = Expense.objects.filter(owner=request.user)

    chart_data = {}
    for exp in user_expenses:
        if exp.category not in chart_data:
            chart_data[exp.category] = float(exp.amount)
        else:
            chart_data[exp.category] += float(exp.amount)

    for category, amount in chart_data.items():
        chart_data[category] = round(amount, 2)
    return JsonResponse(chart_data)


@login_required
def monthly_expenses_pie_chart_data(request):
    user_expenses = Expense.objects.filter(owner=request.user)

    month_num = utils.get_current_date_num('month')
    monthly_expenses = user_expenses.filter(date__month=month_num)

    chart_data = {}
    for exp in monthly_expenses:
        if exp.category not in chart_data:
            chart_data[exp.category] = float(exp.amount)
        else:
            chart_data[exp.category] += float(exp.amount)

    for category, amount in chart_data.items():
        chart_data[category] = round(amount, 2)
    return JsonResponse(chart_data)


@login_required
def expenses_by_month_bar_chart_data(request):
    user_expenses = Expense.objects.filter(owner=request.user)
    months = utils.get_months_list()

    chart_data = {}
    for month in months:
        month_num = months.index(month) + 1
        monthly_expenses = user_expenses.filter(date__month=month_num)

        if monthly_expenses:
            monthly_expenses_sum = round(monthly_expenses.aggregate(
                                    amount=Sum('amount'))['amount'], 2)
            chart_data[month] = monthly_expenses_sum
    return JsonResponse(chart_data)


@login_required
def expenses_by_week_bar_chart_data(request):
    weeks = ['current week', 'last week', '2 weeks ago', '3 weeks ago']
    weeks.reverse()
    
    expenses = [Expense.objects.get_weekly_expense_sum(request.user),
                Expense.objects.get_weekly_expense_sum(request.user, -1),
                Expense.objects.get_weekly_expense_sum(request.user, -2), 
                Expense.objects.get_weekly_expense_sum(request.user, -3)]
    expenses.reverse()

    chart_data = {}
    for i, week in enumerate(weeks):
        chart_data[week] = expenses[i] 
    return JsonResponse(chart_data)


@login_required
def delete_test_user_expenses(request):
    user = str(request.user)

    if user == 'testuser1':
      Expense.objects.delete_testuser_expenses(request)
      return redirect('expenses:home')
    else:
      print('Not allowed to delete the expenses of any user other than testuser1')
      return redirect('expenses:home')