#定義model的class類別之前都需要先import models
#每個class類別都代表一個資料表
from django.db import models
from datetime import date 

# Create your models here.
#Genre:這是圖書館的書的種類的class類別
class Genre(models.Model):
    """
    Model representing a book genre (e.g. Science Fiction, Non Fiction).
    """
    #欄位名稱:name
    #CharField:大概是varchar, nvarchar之類的
    #max_length:此欄位最大長度
    #help_text:此欄位的註解，實務上在公司還真的很少人寫註解在資料表
    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)")
    
    #__str__:Django framework的作法會在每個資料表都定義一個__str__
    #這是用來定義物件最常用的method用的
    #就書的種類來說，當然是取得種類的名稱，因此會直接回傳self.name    
    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name


class Language(models.Model):
    """
    Model representing a Language (e.g. English, French, Japanese, etc.)
    """
    name = models.CharField(max_length=200, help_text="Enter a the book's natural language (e.g. English, French, Japanese etc.)")
    
    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name


#當你的資料表定義包含自定義的function的時候，就必須import reverse
from django.urls import reverse #Used to generate URLs by reversing the URL patterns

class Book(models.Model):
    """
    Model representing a book (but not a specific copy of a book).
    """
    title = models.CharField(max_length=200)
    #ForeignKey:就是讓你在使用QuerySet的時候可以方便的直接連接到外部的class....
    #根據之前的經驗，在一對多或是多對一的時候
    #很容易導致程式碼run到不可預測的地方……不知道Django為什麼要導入ForeignKey
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in the file.
    #TextField:就是一大段的文字
    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN',max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    #ManyToManyField:定義資料表之間多對多的關係，是讓你在使用QuerySet的時候可以方便的直接連接到外部的class
    #但是跟ForeignKey一樣，感覺在production資料一多的時候很可能會run到天荒地老
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')    
    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)
    
    #顯示這本書的所有種類，以逗點區隔，最多三筆
    #而self.genre.all()這部分的程式碼，自動幫你把多對多會用到的中介資料表junction table
    #這部分自動做掉了，算是Django framework優秀的地方
    def display_genre(self):
        """
        Creates a string for the Genre. This is required to display genre in Admin.
        """
        return ', '.join([ genre.name for genre in self.genre.all()[:3] ])
    display_genre.short_description = 'Genre'

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.title
    
    #get_absolute_url:這是自定義的函數，當你使用get_absolute_url的時候
    #會透過book-detail這個url mapping的這個網址mapping規則去導向網頁
    #當然最後會導向的網頁會顯示這個Book物件的詳細細節
    def get_absolute_url(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('book-detail', args=[str(self.id)])        


#uuid:類似GUID的功用, 全世界只會有這麼一組的id
#當你在資料表定義的時候，你的primary key要是使用的是GUID的話
#就要import uuid
import uuid # Required for unique book instances

class BookInstance(models.Model):
    """
    Model representing a specific copy of a book (i.e. that can be borrowed from the library).
    """
    #UUIDField:這就是在Django framework裡面，使用GUID的方式
    #不過～實務上，用這樣子的方式當成primary key的時候，在做join的時候
    #就會搞的自己很頭大就是了
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True) 
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    #LOAN_STATUS:
    #這種寫法用來自定義某某資料表欄位的value的
    #強制定義為m,o,a,r
    #這在傳統的資料庫作法是不可能做到這樣的，加分加分
    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Book availability')

    #ordering:預設的排序方式。可以在Meta的class類別定義
    class Meta:
        ordering = ["due_back"]
        #加上只有圖書館人員專用的權限
        #can_view_all_borrowed_books是此權限的代碼名稱codename
        #one can view all borrowed books是口語化的名稱name
        permissions = (("can_view_all_borrowed_books", "one can view all borrowed books"),) 
        

    def __str__(self):
        """
        String for representing the Model object
        """
        return '{0} ({1})'.format(self.id,self.book.title)        


    from django.contrib.auth.models import User
    #表示借這本書的人是誰
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    #是否到期，自動回傳false or true
    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

class Author(models.Model):
    """
    Model representing an author.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    #DateField:欄位型態是datetime
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ["last_name","first_name"]
    
    def get_absolute_url(self):
        """
        Returns the url to access a particular author instance.
        """
        return reverse('author-detail', args=[str(self.id)])
    

    def __str__(self):
        """
        String for representing the Model object.
        """
        return '{0}, {1}'.format(self.last_name,self.first_name)


