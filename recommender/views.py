
from django.shortcuts import render, redirect
from recommender.models import ThreadModel, MessageModel
from .forms import ThreadForm, MessageForm
from django.views import View
from django.db.models import Q
from django.contrib.auth.models import User
def frontpage(request):
    return render(request, 'recommender/frontpage.html')

'Shows a list of all the people you have messages with'
class ListThreads(View):
    def get(self, request, *arg, **kwargs):
        threads = ThreadModel.objects.filter(Q(user = request.user) | Q(receiver = request.user))

        context = {
            'threads':threads
        }

        return render(request, 'recommender/inbox.html', context)


class CreateThread(View):
    def get(self, request, *args, **kwargs):
       form = ThreadForm()
       context = {
        'form': form
       }

       return render(request, 'recommender/create_thread.html', context)

    '''when a user clicks on the create thread if checks if the person you are sending to exists 
    and then takes you to the message page'''
    def post(self, request, *args, **kwargs):
       form = ThreadForm(request.POST)

       username = request.POST.get('username')

       try:
        receiver = User.objects.get(username = username)
        if ThreadModel.objects.filter(user = request.user, receiver = receiver).exists():
            thread = ThreadModel.objects.filter(user = request.user, receiver = receiver)[0]
            return redirect('thread',pk = thread.pk)
        elif ThreadModel.objects.filter(user = receiver, receiver = request.user).exists():
            thread = ThreadModel.objects.filter(user = receiver, reciever = request.user)[0]
            return redirect('thread', pk = thread.pk)
        if form.is_valid:
            thread = ThreadModel(
                user = request.user,
                receiver = receiver
            )
            thread.save()
            return redirect('thread', pk =thread.pk )
       except:
        return redirect('create-thread')
''' This is the message page where users are able to send messages with each other'''
class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = ThreadModel.objects.get(pk =pk)
        message_list = MessageModel.objects.filter(thread__pk__contains = pk)
        context = {
            'thread': thread,
            'form': form, 
            'message_list': message_list
        }
        return render(request, 'recommender/thread.html', context)
'''This is what sends messages between users '''
class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        thread = ThreadModel.objects.get(pk = pk)
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver
        
        message = MessageModel(
            thread = thread, 
            sender_user = request.user,
            reciever_user = receiver,
            body = request.POST.get('message')
        )
        message.save()
        return redirect('thread', pk = pk)
        


