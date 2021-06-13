from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime #for checking renewal date range.
    
class RenewBookForm(forms.Form):
    #取得表單的input資料
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    #clean_OOXX就是用來驗證這個欄位的
    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']
        
        #Check date is not in past. 
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        #Check date is in range librarian allowed to change (+4 weeks).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data


#利用modelform快速建立create,delete,update功能
#類似asp.net MVC的skeleton
from django.forms import ModelForm
from .models import BookInstance

class RenewBookModelForm(ModelForm):
    #clean_OOXX就是用來驗證這個欄位的
    #ps.OOXX必須為models.py定義的欄位名稱
    def clean_due_back(self):
       data = self.cleaned_data['due_back']
       
       #Check date is not in past.
       if data < datetime.date.today():
           raise ValidationError(_('Invalid date - renewal in past(model form)'))

       #Check date is in range librarian allowed to change (+4 weeks)
       if data > datetime.date.today() + datetime.timedelta(weeks=4):
           raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead(model form)'))

       # Remember to always return the cleaned data.
       return data

    class Meta:
        model = BookInstance
        #下面這是modelform指定單一欄位的方式
        #另有1. fields = '__all__' 或 exclude 的寫法，因此欄位數量很多時，用modelform實做較為方便
        fields = ['due_back']
        #複寫due_back的label名稱
        labels = { 'due_back': _('Renewal date'), }
        help_texts = { 'due_back': _('Enter a date between now and 4 weeks (default 3).'), } 