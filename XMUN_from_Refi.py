    # US Stocks traded on German Gettex.
        # The screen below delivers very limited universe (~250 tickers), which is incorrect (should be ~2000)
            fields = ['TR.ISIN','TR.InstrumentType','TR.CompanyName','TR.ExchangeName','TR.CompanyMarketCap(Scale=9)','TR.TRBCActivity','TR.TRBCEconomicSector']
            US_stocks_on_XMUN = 'SCREEN(U(IN(Equity(active,public,countryprimaryquote))), \
                        IN(TR.ExchangeMarketIdCode,"XMUN"), \
                        IN(TR.RegCountryCode,"US"), \
                        Contains(TR.InstrumentType,"Ordinary Shares"), \
                        CURN=EUR)'
            US_stocks_XMUN, err = ek.get_data(US_stocks_on_XMUN, fields)

        # So in order to do it properly the list of stocks should be taken not via SCREENER, but via Advanced Search manually
            # In advanced search select: Universe = "Equities" & Type of Equity = "Ordinary Shares" & Exchange = "GETTEX" & Country of issuer = "United States"
            # Download to excel and save to csv
            # I saved and scheduled this search to email

            US_stocks_XMUN = pd.read_csv('XMUN_US_Stocks_from_AdvSearch.csv')
            US_STOCKS_XMUN_ISIN = US_stocks_XMUN['ISIN'].tolist()
            US_STOCKS_XMUN_US, err = ek.get_data(US_STOCKS_XMUN_ISIN, ['TR.RIC','TR.TickerSymbol','TR.ExchangeName','TR.CompanyMarketCap(Scale=9)','TR.TRBCEconomicSector'])
            US_STOCKS_XMUN_US.rename(columns={'RIC': 'RIC_main', 'Ticker Symbol': 'Ticker_main','Exchange Name':'Exchange_main','Company Market Cap':'Cap','TRBC Economic Sector Name':'Sector'}, inplace=True)
            
            result = pd.merge(US_stocks_XMUN, US_STOCKS_XMUN_US, on="Instrument")
            result.dropna(axis = "rows", inplace = True)
            result.to_csv('XMUN_US_Stocks.csv')