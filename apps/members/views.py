from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from apps.members.member_manager import MemberManager
from apps.members.forms import MemberForm
from core.exceptions import LibraFlowException, RecordNotFoundException


@login_required
def member_list(request):
    query = request.GET.get("q", "")
    members = MemberManager.search(query)
    paginator = Paginator(list(members), 10)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    return render(request, "members/list.html", {"page_obj": page_obj, "query": query})


@login_required
def member_register(request):
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            try:
                MemberManager.register_member(**form.cleaned_data)
                messages.success(request, "Member registered successfully.")
                return redirect("members:list")
            except LibraFlowException as exc:
                messages.error(request, str(exc))
    else:
        form = MemberForm()
    return render(request, "members/form.html", {"form": form, "mode": "Register"})


@login_required
def member_detail(request, member_id):
    try:
        member = MemberManager.get_member(member_id)
    except RecordNotFoundException:
        messages.error(request, "Member not found.")
        return redirect("members:list")
    from apps.borrow.borrow_manager import BorrowManager
    history = BorrowManager.borrow_history(member_id=member_id)
    return render(request, "members/detail.html", {"member": member, "history": history})


@login_required
def member_delete(request, member_id):
    if request.method == "POST":
        MemberManager.delete_member(member_id)
        messages.success(request, "Member deleted.")
    return redirect("members:list")
