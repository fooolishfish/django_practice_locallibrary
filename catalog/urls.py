from django.urls import path
from django.conf.urls import include
from . import views


urlpatterns = [
    #views.index：使用vews.py裡面定義的function:index()
    #name='index':.html的樣本template檔裡面，要寫href超連結語法的話，就會用到
    path('', views.index, name='index'),
     #加入Books資料表的list清單網頁的url mapping
    path('books/', views.BookListView.as_view(), name='books'),
    #加入Books資料表的詳細資料網頁的url mapping
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    

]

#圖書館管理人員限定的 更新讀者書本到期日的功能
#網址格式：/catalog/book/<bookinstance id>/renew/ 
#renew_book_librarian是底線分隔，表示這是一個function-based view
urlpatterns += [   
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]


urlpatterns += [   
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
]

#圖書館管理人員限定的all borrowed books網頁
urlpatterns += [   
    path('borrowed/', views.AllLoanedBooksListView.as_view(), name='all-borrowed'),
]


#圖書館管理人員限定的 更新讀者書本到期日的功能(改用modelform的方式實做)
#網址格式：/catalog/book/<bookinstance id>/renew_bymodelform/ 
#renew_book_librarian是底線分隔，表示這是一個function-based view
urlpatterns += [   
    path('book/<uuid:pk>/renew_bymodelform/', views.renew_book_librarian_modelform, name='renew-book-librarian-modelform'),
]

#modelform實做範例
#Author資料利用modelform快速建立create, update, delete功能
#modelform的快速建立功能相當類似asp.net mvc的skeleton
urlpatterns += [  
    path('author/create/', views.AuthorCreate.as_view(), name='author_create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author_update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author_delete'),
]

#加入Authors資料表的list清單網頁的url mapping
urlpatterns += [   
    path('authors/', views.AuthorListView.as_view(), name='authors'),
]