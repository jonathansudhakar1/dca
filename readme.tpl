<html>
    <head></head>
    <body>
        <img src="https://github.com/jonathansudhakar1/dca/actions/workflows/buy.yml/badge.svg?event=schedule"/><br/>
        <h1>Dollar Cost Averaging with Leveraged/Inverse Funds</h1>
        <b>⛔ WARNING: This project is purely for experimental purposes and is not investment advise. If you decide to try it, RUN IT ON PAPER ACCOUNT ONLY!⛔</b>
        <hr/>
        <h2>Introduction</h2>
        <p>
        The goal of this experiment is to buy leveraged/inverse funds in regular intervals. For this experiment I will be buying <code>SVIX</code> and <code>FNGU</code> for about $10 each per day. This is a very risky strategy and using real money is not recommended.
        <br>
        I could not find a broker that supports automatic recurring investments in leveraged funds or one that has an api and supports fractional shares. Most brokers like Robinhood and Webull that support recurring investments do not support recurring investments in leveraged or inverse funds. Large brokers that do have APIs like Tradestation and IKBR do not allow fractional shares. M1 Finance does not support <code>SVIX</code> and <code>FNGU</code>. Alpaca is the only broker that I found that supports fractional shares (not for <code>SVIX</code> at the time of writing) but they don't let you deposit money in the account in regular intervals. For this experiment I will stick with Alpaca because I don't have a better option. 
        <ul>
            <li><code>SVIX</code> - 1x VIX Short Term Futures ETN - 1 share every Tuesday and Thursday since they don't support fractional shares.</li>
            <li><code>FNGU</code> - 3x FANG+ ETN - $10 worth everyday</li>
        </p>
        <hr/>
        <h2>Testing</h2>
        To run the scipt, you would need to install dependencies by running the following command:
        <pre>pip install -r requirements.txt</pre>
        You would need the following environment variables:
        <ul>
            <li><code>ALPACA_ENDPOINT</code> set to <code>https://paper-api.alpaca.markets</code> </li>
            <li><code>ALPACA_KEY_ID</code></li>
            <li><code>ALPACA_SECRET</code> </li>
        To buy an asset, you would need to run the following command like:
        <pre>python main.py --symbols FNGU=\$10 SVIX=1</pre>
        <p>The <code>--symbols</code> argument takes an array of key-value pairs where the key is the asset's symbol and value is the number of shares to buy or notional value in dollars (prefixed with $)</p>
        <hr>
        <h2>Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Asset</th>
                    <th>Average Price</th>
                    <th>Current Price</th>
                    <th>ROI</th>
                    <th>&#128200;</th>
                </tr>
            </thead>
            <tbody>
                %for item in positions:
                    <tr>
                        <td>{{ item.symbol }}</td>
                        <td>${{ item.avg_entry_price }}</td>
                        <td>${{ item.current_price }}</td>
                        <td>{{ "{:.2%}".format(float(item.unrealized_plpc)) }}</td>
                        <td>{{ "&#128994;&#128515;" if float(item.unrealized_plpc) > 0 else "&#128308;&#128546;" }}</td>
                    </tr>
                %end
            </tbody>
            <tfoot>
                <tr>
                    <td><b>Total</b></td>
                    <td></td>
                    <td></td>
                    <td><b>{{ "{:.2%}".format(float(total_change_pct)) }}</b></td>
                    <td>{{ "&#128994;&#128518;" if float(total_change_pct) > 0 else "&#128308;&#128557;" }}</td>
                </tr>
            </tfoot>
        </table>
        <h3>PnL over time (calculations may not be accurate):</h3>
        <img src="history.png"/>

        <hr>

        <p>Updated at {{ updated_at }}</p>
    </body>
</html>