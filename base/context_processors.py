from .models import *


def global_var(request):
    notifications = None
    if request.user.is_authenticated:
        if not request.user.is_staff:
            notifications = NotificationUser.objects.filter(
                user=request.user, read=False).order_by('-create_date')
        else:
            notifications = NotificationAdmin.objects.filter(
                read=False).order_by('-create_date')

    # if request.user.is_superuser or not request.user.is_staff:
    #     unread_orders = Order.objects.filter(completed=True, track=1).count()
    # else:
    #     unread_orders = Order.objects.filter(
    #         user__profile__expert=request.user.expert, completed=True, track=1).count()

    context = {'notifications': notifications}
    return context
