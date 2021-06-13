from django.shortcuts import render

# Create your views here.
from .models import Book, Author, BookInstance, Genre

#def index()是function-based view，因此需利用＠login_required decorator來做網頁驗證
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # The 'all()' is implied by default.
    num_book_title_icontain_how = Book.objects.filter(title__icontains = 'how').count()
    
    #這是利用session來記錄訪客的來訪次數
    # Number of visits to this view, as counted in the session variable.
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1
    
    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        #index()最後將會導向到下列這個.html檔案:index.html
        'index.html',
        #並且把剛剛從db取得的物件傳送到index.html
        # context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors},
        # context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors,'num_book_title_icontain_how':num_book_title_icontain_how},
        
        #把session的num_visits變數也加進去
        context={'num_books':num_books,'num_instances':num_instances,
        'num_instances_available':num_instances_available,'num_authors':num_authors,
        'num_book_title_icontain_how':num_book_title_icontain_how,'num_visits':num_visits},
    )

    #建立Book資料的List清單網頁
from django.views import generic

class BookListView(generic.ListView):
    model = Book
    
    #等等要去哪個路徑找.html檔案
    #不定義這個template_name的話，Django就會去預設的路徑尋找.html
    #預設的路徑是：/locallibrary/catalog/templates/catalog/book_list.html
    #不過目前暫時程式碼設定路徑的方式跟預設一樣就好    
    template_name = '/locallibrary/catalog/templates/catalog/book_list.html'

    #get_context_data()是用來建立自訂的Server side variable的
    #跟.Net MVC也挺像的
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context

    #這是分頁機制, 以下設定一頁的最多資料筆數 = 1
    paginate_by = 1  

#從db取得某本Book的明細資料
#不需要寫什麼特殊的Query語法，Django將會自動做好binding
class BookDetailView(generic.DetailView):
    model = Book   

class AuthorDetailView(generic.DetailView):
    """
    Generic class-based detail view for an author.
    """
    model = Author    


#renew_book_librarian用於讀書館員幫讀者手動更新書的到期日	
from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm

#加上適當的權限，限制此功能只有圖書館員可使用
@permission_required('catalog.can_edit_all_borrowed_books')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
	#執行query到db找這筆資料
    #找不到這筆資料的話，會丟出404網頁錯誤
    book_inst=get_object_or_404(BookInstance, pk = pk)

	#if post == true, 表示是user編輯完畢
    # If this is a POST request then process the Form data
    if request.method == 'POST':

		# 透過forms.py去驗證使用者提交的欄位value是否合法
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

		#透過reverse，可以將url.py的name轉成實際的網址
        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

	#if post == false, 表示是user初次載入這個編輯頁，僅給予一些欄位預設value而已
    #預設給讀者多三個禮拜的時間續借			
    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})    

#限制LoanedBooksByUserListView功能必須登入：LoginRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user. 
    """
    model = BookInstance
    #自定義.html檔案的路徑，這次不使用預設路徑了！
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

#僅圖書館工作人員librarian可確認所有已經借出的書籍
from django.contrib.auth.mixins import PermissionRequiredMixin

class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    #這個系統功能需要有can_view_all_borrowed_books權限
    permission_required = 'catalog.can_view_all_borrowed_books'
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_all.html'
    def get_queryset(self):
        #排序order by due_back desc
        return BookInstance.objects.filter(status__exact='o').order_by('-due_back')
    paginate_by = 10

    #renew_book_librarian用於讀書館員幫讀者手動更新書的到期日
#****************改用modelform的方式實做！***********
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

#用modelform方式實做的話，與之前的差異點：需改 import RenewBookModelForm
#from .forms import RenewBookForm
from .forms import RenewBookModelForm

def renew_book_librarian_modelform(request, pk):
    
    book_inst=get_object_or_404(BookInstance, pk = pk)
  
    if request.method == 'POST':
      
        #用modelform方式實做的話，與之前的差異點：需改用RenewBookModelForm去做欄位驗證
        #form = RenewBookForm(request.POST)     
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():            
            
            #用modelform方式實做的話，與之前的差異點：欄位名稱需改成due_back
            #book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.due_back = form.cleaned_data['due_back']
            book_inst.save()
            
            return HttpResponseRedirect(reverse('all-borrowed') )
    
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)

        #用modelform方式實做的話，與之前的差異點：欄位名稱需改成due_back
        # form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian_modelform.html', {'form': form, 'bookinst':book_inst})   

#modelform實做範例
#利用Django的skeleton快速建立create, update, delete功能
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(CreateView):
    model = Author
    #選取Author資料表全部的欄位
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}

class AuthorUpdate(UpdateView):
    model = Author
    #選取特定欄位
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    #刪除成功之後，自動導向到下列的網址
    success_url = reverse_lazy('authors')

#建立Author資料的List清單網頁
from django.views import generic

#這是class-based views的限制網頁必須登入的作法
from django.contrib.auth.mixins import LoginRequiredMixin
class AuthorListView(LoginRequiredMixin, generic.ListView):

# class AuthorListView(generic.ListView):
    model = Author
    #透過定義get_queryset()就可以自己定義想要的資料
    #沒有要自定義的話就註解掉get_queryset()
    def get_queryset(self):
        # return Author.objects.filter(title__icontains='bike')[:5] #取前五筆資料，title包含關鍵字'bike'的
        return Author.objects.filter()[:100] #取前100筆資料
    #等等要去哪個路徑找.html檔案
    #不定義這個template_name的話，Django就會去預設的路徑尋找.html
    #預設的路徑是：/locallibrary/catalog/templates/catalog/author_list.html
    #不過目前暫時程式碼設定路徑的方式跟預設一樣就好    
    template_name = '/locallibrary/catalog/templates/catalog/author_list.html'

    #get_context_data()是用來建立自訂的Server side variable的
    #跟.Net MVC也挺像的
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(AuthorListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context

    #這是分頁機制, 以下設定每頁最多10筆資料
    paginate_by = 10        