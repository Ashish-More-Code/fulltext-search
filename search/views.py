from django.shortcuts import render, HttpResponse
from search.models import *
from django.contrib.postgres.search import SearchVector, SearchQuery ,SearchRank

# Create your views here.
def index(request):
    search=request.GET.get('search')
    if search:
        # vector=SearchVector('title','description','category')
        vector=(
            SearchVector('title',weight='A')+
            SearchVector('description',weight='B')
        )
        query=SearchQuery(search)
        rank=SearchRank(vector,query)

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

        product=Product.objects.annotate(search=SearchVector('title','description','category')).filter(search=search)
        # product=Product.objects.annotate(rank=rank).order_by('-rank').filter(rank__gte=0.02)
        # product=Product.objects.annotate(rank=rank).order_by("-rank")
        # for i in product:
        #     print(i.rank)

    else:
         product=Product.objects.all()

    context={'results':product,'search':search}
    return render(request,"index.html",context)    