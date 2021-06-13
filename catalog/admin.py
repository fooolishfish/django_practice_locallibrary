from django.contrib import admin

# Register your models here.

from .models import Author, Genre, Book, BookInstance, Language


#admin.site.register(Author)
# admin.site.register(Book)
# admin.site.register(BookInstance)
admin.site.register(Genre)
admin.site.register(Language)

################################################################
#自行練習Author + BookInline的同時編輯
class BookInline(admin.TabularInline):
    model = Book
    extra = 1
################################################################


#以下有進階的admin作法
#首先從Author開始

################################################################
#AuthorAdmin:Author的admin的進階作法
# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    #list_display:是用來overwrite Author類別的__str__(self)函式的
    #原本__str__(self)只是用來顯示lastname + firstname而已
    #現在改寫成lastname, firstname, date_of_birth, date_of_death
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    
    #fields:
    #用來基本客製化顯示的欄位的順序（編輯資料時）
    #預設的系統排列方式，是垂直的一個一個欄位顯示
    #以下的方式，就可以把date_of_birth, date_of_death放在同一列
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]

    #pass表示AuthorAdmin不變更原本Author類別的行為
    #當不打算變更原本Author類別的行為的時候，寫pass就可以了
    # pass

    #自行練習Author + BookInline的同時編輯
    inlines = [BookInline]


# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)
################################################################


################################################################
#BooksInstanceInline:
#這是讓Book可以同時跟BooksInstance
#被編輯的大絕招，不用像以前那樣，自己要把Book跟BookInstance的PK關連起來才能顯示
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 1
################################################################

################################################################
#BookAdmin:
# Register the Admin classes for Book using the decorator

#補充：@admin.register跟admin.site.register完全一模一樣的功用
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    #這裡也是overwrite Book類別的__str__()函式
    #只是這裡有個foreign key是genre圖書種類，我們採用呼叫Book類別裡面的
    #method:display_genre()組合字串來顯示這個foreign key物件
    #而由於Book與Genre類別的關係是many to many
    #所以display_genre()自動把中介資料表junction table這部分，自動作掉了
    #算是Django framework優秀的地方
    list_display = ('title', 'author', 'display_genre')    

    #BooksInstanceInline:
    #這是讓Book可以同時跟BooksInstance
    inlines = [BooksInstanceInline]    
    #pass

################################################################


################################################################
#BookInstanceAdmin:
# Register the Admin classes for BookInstance using the decorator

@admin.register(BookInstance) 
class BookInstanceAdmin(admin.ModelAdmin):    
    #pass
    list_display = ('book', 'status','borrower', 'due_back', 'id')   
    #在畫面旁邊加入過濾條件的欄位
    list_filter = ('status', 'due_back')

    #fieldsets:
    #用來進階客製化的欄位排序以及大標題(大標題可以為空)（編輯資料時）
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )