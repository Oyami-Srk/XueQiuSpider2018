# README (No one will read me)
--------------------------------------

Project Name: **S**~~now~~**B**~~all~~ **Spider**

Project Author: **OyaKti Studio**

Project Status: **Working**


> Bitbucket DO NOT support org-file which is better than markdown.


To make everything easy, I will descrirbe all functions with no **__** at the beginning/end of the name.  
(Using the same pattern can make description more understandable.)  

* FunctionToDo  (TODO)  
    Param:  
        1. xxxxxx(... default=...): ...  
        2. blabla(...): ...  
    Return:  
        ...  
    Comment:  
        ...  

## FetchPortfolio.py:  
  
* GetRateChartAsDataframe  
    Param:   
        1. Symbol(str): Portfolio's symbol, like 'ZH123456'. (The same below)  
        2. noPercent(bool default=True): If that's True, spider won't get percent in rate chart.   
    Return:  
        A dataframe which carries a single portfolio's everyday value and percent(if you set noPercent False)  
    Comment:  
        
* GetRateChartsAsDataframe  
    Plural form of GetRateChartAsDataframe  
    Param:   
        1. Symbols(list of strs): Portfolio's symbols, like ['ZH123456', 'ZH654321']. (The same below)  
        2. noPercent(bool default=True)  
    Return:  
        A dataframe which carries portfolios' everyday value and percent(if you set noPercent False)  
    Comment:  
        Function which has the same name as other but a 's' does the same thing but reciving a list(names xxxx*s*) return a list or a dataframe carries complex sheets. Those functions are called 'Plural form'.  
    
* SaveRateChartToHDF5  
    Saver form of GetRateChartAsDataframe, default="RateChart.h5"  
    Param:  
        1. Symbol(str)  
        2. Path(str default="RateChart.h5"): The path of hdf5 file.  
        3. noPercent(bool default=True)  
    Return:  
        No return  
    Comment:  
        Those functions which save the other function's return and simply append a parameter like 'filename/Path' are called 'Saver form'  
      
* SaveRateChartsToHDF5  
    Plural form of SaveRateChartToHDF5  
      
* GetMarketList  
    Param:  
        1. market(str default='cn')  
        2. profit(str default='monthly_gain')  
        3. sort(str default='best_benefit')  
        4. sale_flag(**str** default='0')  
        5. stock_posistions(**str** default='0')  
    Return:  
        A list of orderly portfolios' symbols.  
    Comment:  
        Param "market": cn/us/hk  
        Param "profit": monthly_gain/daily_gain/annualized_gain_rate  
        Param "sort": best_benefit/grow_fast/win_market  
        Param "sale_flag": Include(0) Gem or not(1)  
        Param "stock_positions": Filter out portfolio with single stock(1) or not(0)  
      
* GetMarketListInfo  
    Param:  
        1. market(str default='cn')  
        2. profit(str default='monthly_gain')  
        3. sort(str default='best_benefit')  
        4. sale_flag(**str** default='0')  
        5. stock_posistions(**str** default='0')  
    Return:  
        A dataframe which carries the informations about every portfolios in Market list.  
    Comment:  
        See also GetMarketList  
          
* SaveMarketListInfo  
    Saver form of GetMarketListInfo, default='portfolio_summary.h5'  
      
* GetPortfolioMarket  
    Param:  
        1. Symbol(str)  
    Return:  
        A string of market symbol.  
    Comment:  
      
* CheckPortfolioClosed  
    Param:  
        1. Symbol  
    Return:  
        A bool value of whether portfolio is cloesd(True) or not(False)  
    Comment:   
      
* GetAllPortfolio  
    Param:  
        1. market(str default='cn')  
        2. closed(bool default=False)  
        3. Min(int default=0)  
        4. Max(int default=1300000)  
    Return:  
        A list of all eligible portfolio.  
    Comment:  
        100 portfolios will take 30 seconds.   
          
* GetPortfolioInfo  
    Param:  
        1. Symbol(str)  
    Return:  
        A dictionary which carries information about portfolio.  
    Comment:  
        `  
        return {'day': day,  
                'month': month,  
                'net': net,  
                'total': float('%.4f' % total),  
                'market': GetPortfolioMarket(Symbol),  
                'closed': CheckPortfolioClosed(Symbol),  
                'turnover_3m': turnover_3m,  
                'turnover_12m': turnover_12m,  
                'liquidity_3m': liquidity_3m,  
                'liquidity_12m': liquidity_12m  
                }  
        `

* GetPortfoliosInfo
    Plural form of GetPortfolioInfo
