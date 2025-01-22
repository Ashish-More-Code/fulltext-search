from django.shortcuts import render, HttpResponse
from search.models import *
from django.db.models import Q
from django.contrib.postgres.search import (SearchVector, SearchQuery ,SearchRank ,TrigramSimilarity)
from django.views.decorators.cache import cache_page
from django.core.cache import cache


# Create your views here.
def index(request):
    search=request.GET.get('search')
    if search:
        '''
        __search
        lookup means by which method you want to filter data in queryset
        1>This is search lookup in this search vectore is created using field or column which you provide 
        and search query is created using user inputed text in search field
        2>finally search query and vectore compared and matching data is returned
        3>product=Product.objects.filter(title__search=search)
        '''

        '''
        searchvector()
        if you want to search data by comparing in multiple fields then we use search vector
        1>SearchVector('title','description','category')
        2>in this we create vectore and search query is created using user inputed text in search field
        3>then results are obtained using comparisong of vector and query
        4>product=Product.objects.annotate(search=SearchVector('title','description','category')).filter(search=search)
                                                |this is used to filter in filter(search=user inputed value for search)
        '''

        '''
        searchquery(text,search_type='phrase' default is plain text)
        >>> SearchQuery("red tomato")  # two keywords
        >>> SearchQuery("tomato red")  # same results as above
        >>> SearchQuery("red tomato", search_type="phrase")  # a phrase
        >>> SearchQuery("tomato red", search_type="phrase")  # a different phrase
        it just improve the qulity of search term provided by user in search field
        1>SearchQuery converts the user input into a format that PostgreSQL’s full-text search engine can process. 
        It ensures the search terms are interpreted correctly, handling nuances like stemming, stop words, and lexemes.
        2>SearchQuery translates the terms the user provides into a search query object that the database compares to a search vector.
        By default, all the words the user provides are passed through the stemming algorithms, 
        and then it looks for matches for all of the resulting terms. 
        '''

        '''Searrank(searchvectore,serchquery (here we pass this two))
        1>In this we annotate the relavency query object calculated by serch rank based on vectore and query.
        2>this will provide more relevent data as result.
        query=Searchquery(text,search_type='phrase' default is plain text)
        vectore=Searchvectore(columns or fields)
        rank=searchrank(vectore,query)
        3>product=Products.objects.annotate(rank=rank).order_by('-rank')
        4> here we also provide in vectore that which filed while serching will get more weightage or importance
         vector=(
            SearchVector('title',weight='A')+
            SearchVector('description',weight='B')
        )
        '''
        '''
        Trigram similarity.
        When user make spelling mistakes then its usefull.
        This extension allows you to perform trigram similarity lookups, 
        which are useful for handling typographical errors and approximate searches.
        we need to install extension in postgress database CREATE EXTENSION pg_trgm;
        '''
       
        
        query = SearchQuery(search)
        vector =  SearchVector(
            "title",
            "description",
            "category",
            "brand"
        )
        brands=[]
        category=[]
        rank = SearchRank(vector, query)
        product = Product.objects.annotate(rank=rank,similarity=TrigramSimilarity('title',search)+
        TrigramSimilarity('description',search)).filter(Q(similarity__gte=0.05)&Q(rank__gte=0.05))
        if cache.get("brands"):
            category=cache.get("brands")
        else:
            cache.set("brands", Product.objects.all().distinct('brand').order_by('-brand'), 60*1)
        if cache.get("category"):
            category=cache.get("category")
        else:
            cache.set("category", Product.objects.all().distinct('category').order_by('-category'), 60*1)

        
    else:
        brands=[]
        category=[]
        product=Product.objects.all()
        if cache.get("brands"):
            category=cache.get("brands")
        else:
            cache.set("brands", Product.objects.all().distinct('brand').order_by('-brand'), 60*1)
        if cache.get("category"):
            category=cache.get("category")
        else:
            cache.set("category", Product.objects.all().distinct('category').order_by('-category'), 60*1)




    if request.GET.get('min_price') and request.GET.get('max_price'):
        minprice=request.GET.get('min_price')
        maxprice=request.GET.get('max_price')
        product=Product.objects.filter(price__lte=maxprice,price__gte=minprice)

    if request.GET.get('category'):
        cat=request.GET.get('category')
        if cache.get("product"):
            product=cache.get("product")
        else:
            cache.set("product", Product.objects.filter(category=cat), 60*1)
        
    context={'results':product,'search':search,'brands':brands,'category':category}
    return render(request,"index.html",context)    