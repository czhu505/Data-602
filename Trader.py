# -*- coding: utf-8 -*-
"""
Created on Sun Mar  4 18:30:05 2018

@author: Zhu
"""
import pandas as pd
import  requests
from bs4 import BeautifulSoup
import re
from json import loads
import warnings
warnings.filterwarnings("ignore")
import time
#from collections import deque



#updateprice() for geting a instant ask and bit price
#return (tick,askprice,bidprice,time.strftime("%c")) to Trade()
def updateprice(tick):
    url= "http://finance.yahoo.com/quote/" + tick +"/profile?p=" +tick
    soup = BeautifulSoup(requests.get(url, "lxml").content)
    script = soup.find("script",text=re.compile("root.App.main")).text
    data = loads(re.search("root.App.main\s+=\s+(\{.*\})", script).group(1))
    stores = data["context"]["dispatcher"]["stores"]
    text=stores[u'QuoteSummaryStore']
    askprice=float(text["summaryDetail"]["ask"]["fmt"].replace(",",""))
    bidprice=float(text["summaryDetail"]["bid"]["fmt"].replace(",",""))
    newprice=(tick,askprice,bidprice,time.strftime("%c"))
    return (newprice)


#updateprice(ticker, askprice, bidprice) gets update price for stock right at the moment, 
#and data type is tuple
#if quantity is positive, recorde add as buy stock with ask price
#tup=(side,quantity,ticker,a,cost,time.strftime("%c")) gets data of executive trade
#histlist.append(tup) add new trad to hist tuple list, data type is tuple  
#updatePL(tup,pl,account_remain) caluculat profit/loss after adding a new trade
#return (histlist,pllist,amount,Time) to main()
 
def Trade(histlist,pllist,amount):
    
    ticker=str(input("Enter a ticker ( AAPL, AMZN, INTC, MSFT, SNAP) : "))
    ticker=ticker.upper()
    t,a,b,T =updateprice(ticker)
    print(T)
    print("Asking price : " )
    print(a)
    print("Biding price : " )
    print(b)
    
    #The user is then asked to confirm the trade at the market price by enter the quantity.
    while True:
        try:
             quantity=int(input("Enter number of share(s) (positive for buy/ negative for sell / 0 back to manu): ")) 
             break
        except ValueError:
             print("Wrong input! Try again.")
             
    if quantity !=0 :  
        tic,a,b,T=updateprice(ticker) 
        
        if quantity>0:
            while(amount<(a*quantity)):
                print("You don't have enought money in your account. ")
                quantity=int(input("Enter number of share(s) (positive for buy/ negative for sell / 0 back to manu): ")) 
                
            cost= a * quantity 
            tup=("buy",quantity,tic,a,cost,T)
            histlist.append(tup)
            
            tup,pllist=updatePL(tup,pllist)
            
            print(T)
            print("Number shares you buy : ")
            print(quantity) 
            print("Total cost : ")
            print(a*quantity) 
            amount=amount-b*quantity
            
            
        #if quantity is negative, recorde add as sell stock with bid price
        elif quantity<0 :
            cost= b * quantity
            tup=("sell",quantity,tic,b,cost,T)
            histlist.append(tup)
            tup,pllist=updatePL(tup,pllist)
            
            print(T)
            print("Number shares you sell : ")
            print(quantity) 
            print("Total cost : ")
            print(b*quantity) 
            amount=amount-b*quantity

    return(histlist,pllist,amount)


#when new trad executive, call updataPL(), calculate the profit and loss and update cash amount in account
#newtup has items as in ("buy",quantity,ticker,price,cost,time.strftime("%c")) 
#pllist has items as in ['Ticker', Inventory, Rpl,Upl,'Time',Wap]
#each ticker only has maximun 1 recorde in the table  
#rPL updated only when sell stocks            
def updatePL(newtup,pllist):
    
    side,quant,ticker,price,cost,time = newtup
    temp=[]
    temp=[i for i in pllist if i[0] == ticker]
    
    if not temp:
            newpl=(ticker,quant,0.00,0.00,time, price) 
            pllist.append(newpl) 
        
    else:
            pllist= [i for i in pllist if i != temp[0]]
            oticker,oinventry,oRpl,oUpl,otime,owap = temp[0]
            
            #For RPL: if it is long position, selling uses bid price 
            if quant<0 and oinventry>0:
                Rpl=(price-owap)*min(abs(quant),abs(oinventry))
                
            #if it is short position, buying use ask price 
            elif quant>0 and oinventry<0:
                Rpl=(owap-price)*min(abs(quant),abs(oinventry))    
            
            else:
                Rpl=0.0
         
            #For wap (is absolute positive representing a signle price of share of buy and sell:
            inven=oinventry+quant
            if( inven!=0):
                wap=(owap*oinventry+price*quant)/inven    
            else:
                wap=0.00
                
            newpl=(ticker,inven,Rpl,0.0,otime, wap)
            pllist.append(newpl)
        
    return(newtup,pllist)
    
      
      
#freshUPL() undated only when user selction Show P/L .      
#freshUPL() is to update the unreal profit/loss using updated ask/bid price to est.
#Upl is only data will be changed regarding to exist ticker.
#updateprice() has (tick,askprice,bidprice,time.strftime("%c"))
#pllist has items as in ['Ticker', Inventory, Rpl,Upl,'Time',Wap]
#inventory is negative, to cover short sell, upl use ask price; else use bid price.

def showPL(pllist):
   
     apple=updateprice("AAPL")
     amazon=updateprice("AMZN")
     intel=updateprice("INTC")
     microsft=updateprice("MSFT")
     snapchat=updateprice("SNAP")
    
     renewlist= [apple, amazon, intel,microsft,snapchat]
    
     for i, pltup in enumerate(pllist):
         for j, listtup in enumerate(renewlist): 
         #if ticker pllist item exist in renewlist, update upl
               if pltup[0] == listtup[0]:
                       
                       temp=pltup
                       ticker,inventry,Rpl,Upl,time,wap=temp
                     
                       pllist= [i for i in pllist if i != temp]
                       
                       #For long position, upl use bid price
                       if inventry>0:
                           Upl=(listtup[2]-wap)*inventry
                           
                       #For short position, upl use ask price; else upl use ask price  
                       elif inventry<0 :
                           Upl=(wap-listtup[1])*inventry
                       
                       else: 
                           Upl=0.0
                           wap=0.0
                   
                       newtup=(ticker,inventry,Rpl,Upl,time,wap)    
                       pllist.append(newtup)
     return(pllist)

    
    
if __name__=="__main__":
    
    print("\n")
    # hist data typy is tuple, it will convert to 
    #history DataFrame(hist,columns = ['Side', Volumne,'Ticker',Price,Cost,'Time'])  
    hist=[]
    
    #pl data typy is tuple , it will convert to 
    #pltable DataFrame(pl,columns = ['Ticker', Inventory, Rpl,Upl,'Time',Wap])
    pl=[]
    
    
    #account recordes amount of the cash, will update after placing executive trade
    account=1000000.00
    
    print("Your cash account : ")
    print(account)
    
    option=1 
    
    while option != 4 :
            print("\n")
            print("======================================")
            print("                 Menu                 ")
            print("======================================")
            print("             1.  Trade                ")
            print("             2.  Show Blotter         ")
            print("             3.  Show P/L             ")
            print("             4.  Quit                 ")
            print("======================================")
            
            #catch a wrong input at one times 
            while True:
                try:
                     option = int(input("Please enter a number (1-4): "))  
                     break
                except ValueError:
                     print("Wrong input! Try again.")
                         
            while(option<1 or option >4) :
                print("Wrong number! Try again.")
                print("\n")
                option = int(input("Please enter a number (1-4): ")) 
        
        
            #The user will then be given the list of 5 equities they can trade and be allowed to pick one and state a quantity. 
            #The user is then asked to confirm the trade at the market ask price scraped from Yahoo.
            if (option==1): 
                hist,pl,account= Trade(hist,pl,account)
                
                print("_________________________________________________")

            
            #Displays the trade blotter, a list of historic trades made by the user. The trade blotter will display
            #the following trade data, with the most recent trade at the top
            elif (option==2):
                if not hist:
                    print("\n")
                    print("No trading record.")
                    print("\n")
                    print("Your cash account : ")
                    print(account)
                else:    
                    history=pd.DataFrame(hist,columns = ['Side', 'Volumne','Ticker','Price','Cost','Time'])  
                    print("\n")
                    print("======================================")
                    print("            Trading History           ")
                    print("======================================")
                    print(history.iloc[::-1])
                print("_________________________________________________")

            #Displays the profit / loss statement. The P/L will display, 
            #the following trade data, with the most recent trade at the top 
            #Ticker, Position, Current Market Price, VWAP, UPL (Unrealized P/L), RPL (Realized P/L)
            
            elif (option==3):
                if not hist:
                    print("\n")
                    print("No trading record.")
                    print("\n")
                    print("Your cash account : ")
                    print(account)
                else:
                    pl=showPL(pl)
                    print("\n")
                    print("======================================")
                    print("              Profit/Loss             ")
                    print("======================================")
                    pltable=pd.DataFrame(pl,columns = ['Ticker', 'Inventory', 'Rpl','Upl','Time','Wap'])
                    print(pltable.iloc[::-1])
                    print("\n")
                    print("Your cash account : ")
                    print(account)
                    
                print("_________________________________________________")   
                    
            #Quit when option==4 
            else: 
                print("Good Luck!")
                print("_________________________________________________")
                

 