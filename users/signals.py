from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender='users.TransactionHistory')
def update_credit(sender, instance, **kwargs):
    if instance.status == 'AC':
        user_receiver = instance.user_receiver
        user_sender = instance.user_sender
        user_receiver.credit += instance.price
        user_receiver.save()
        if user_sender:
            user_sender.credit -= instance.price
            user_sender.save()
