from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
import json

class CryptoTrackerApp(App):
    def build(self):
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 1. Navigation Panel
        nav_panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=5)
        self.btn_tab1 = Button(text="Direct Pairs (Tab 1)", background_color=(0.1, 0.6, 0.4, 1))
        self.btn_tab2 = Button(text="Cross Matrix (Tab 2)", background_color=(0.2, 0.2, 0.2, 1))

        self.btn_tab1.bind(on_press=self.switch_to_tab1)
        self.btn_tab2.bind(on_press=self.switch_to_tab2)

        nav_panel.add_widget(self.btn_tab1)
        nav_panel.add_widget(self.btn_tab2)
        self.main_layout.add_widget(nav_panel)

        self.current_tab = 'tab1'

        # 2. Table Headers (5 Columns)
        self.grid_header = GridLayout(cols=5, size_hint_y=None, height=40, spacing=2)
        self.main_layout.add_widget(self.grid_header)

        # 3. Scrollable Grid Area
        self.scroll_view = ScrollView()
        self.data_grid = GridLayout(cols=5, size_hint_y=None, spacing=2)
        self.data_grid.bind(minimum_height=self.data_grid.setter('height'))
        self.scroll_view.add_widget(self.data_grid)
        self.main_layout.add_widget(self.scroll_view)

        # 4. Input Panel
        self.input_panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.pair_input = TextInput(hint_text="Enter base token (e.g., SOL)", multiline=False, font_size="16sp", size_hint_x=0.6)
        add_button = Button(text="Add Coin", font_size="16sp", size_hint_x=0.4)
        add_button.bind(on_press=self.add_custom_coin)
        self.input_panel.add_widget(self.pair_input)
        self.input_panel.add_widget(add_button)
        self.main_layout.add_widget(self.input_panel)

        # Master Data Repositories
        self.fixed_pairs = {"BTCUSDT": 63100.72, "ETHUSDT": 1770.39, "BNBUSDT": 578.27, "SUIUSDT": 0.7350}
        self.known_matrix_coins = {"BTC", "ETH", "BNB", "SUI"}
        self.matrix_pairs = {}

        # UI Reference Dictionary to prevent widget rebuild crashes
        self.ui_references = {}

        self.update_headers()
        Clock.schedule_once(self.initialize_application, 0.5)

        return self.main_layout

    def update_headers(self):
        self.grid_header.clear_widgets()
        headers = ["Pair", "Fixed Price", "Live Price", "Change %", "Action"] if self.current_tab == 'tab1' else ["Cross Pair", "Fixed Ratio", "Live Cross", "Change %", "Action"]
        for h in headers:
            self.grid_header.add_widget(Label(text=h, font_size="14sp", halign="center"))

    def switch_to_tab1(self, instance):
        if self.current_tab == 'tab1': return
        self.current_tab = 'tab1'
        self.btn_tab1.background_color = (0.1, 0.6, 0.4, 1)
        self.btn_tab2.background_color = (0.2, 0.2, 0.2, 1)
        self.update_headers()
        self.rebuild_ui_layout_structures()

    def switch_to_tab2(self, instance):
        if self.current_tab == 'tab2': return
        self.current_tab = 'tab2'
        self.btn_tab1.background_color = (0.2, 0.2, 0.2, 1)
        self.btn_tab2.background_color = (0.1, 0.6, 0.4, 1)
        self.update_headers()
        self.rebuild_ui_layout_structures()

    def initialize_application(self, dt):
        self.rebuild_matrix_dictionary()
        self.rebuild_ui_layout_structures()
        Clock.schedule_interval(self.refresh_live_data_only, 3.0)

    def rebuild_matrix_dictionary(self):
        self.matrix_pairs.clear()
        coins = list(self.known_matrix_coins)
        for i in range(len(coins)):
            for j in range(len(coins)):
                if i == j: continue
                base, quote = coins[i], coins[j]
                base_fixed = self.fixed_pairs.get(f"{base}USDT", 1.0)
                quote_fixed = self.fixed_pairs.get(f"{quote}USDT", 1.0)
                self.matrix_pairs[f"{base}/{quote}"] = base_fixed / quote_fixed

    def rebuild_ui_layout_structures(self):
        """Builds components safely once"""
        self.data_grid.clear_widgets()
        self.ui_references.clear()

        target_dataset = self.fixed_pairs.items() if self.current_tab == 'tab1' else self.matrix_pairs.items()

        for key, fixed_value in list(target_dataset):
            # Col 1: Label
            self.data_grid.add_widget(Label(text=key, font_size="13sp", height=38, size_hint_y=None))

            # Col 2: Stable, Non-wiped input
            txt_input = TextInput(text=f"{fixed_value:.4f}", multiline=False, input_filter='float',
                                  font_size="13sp", height=36, size_hint_y=None,
                                  background_color=(0.15, 0.15, 0.15, 1), foreground_color=(1, 1, 1, 1))
            txt_input._row_key = key
            txt_input.bind(text=lambda instance, val: self.on_fixed_price_edit(instance._row_key, val))
            self.data_grid.add_widget(txt_input)

            # Col 3 & 4: Labels we can manipulate directly via references
            live_label = Label(text="Loading...", font_size="13sp", height=38, size_hint_y=None)
            change_label = Label(text="0.00%", font_size="13sp", height=38, size_hint_y=None, markup=True)

            self.data_grid.add_widget(live_label)
            self.data_grid.add_widget(change_label)

            # Col 5: Remove Button
            rem_btn = Button(text="X", font_size="12sp", height=34, size_hint_y=None, background_color=(0.8, 0.2, 0.2, 1))
            rem_btn._row_key = key
            rem_btn.bind(on_press=lambda instance: self.remove_coin_completely(instance._row_key))
            self.data_grid.add_widget(rem_btn)

            # Store pointers to modify text blocks dynamically
            self.ui_references[key] = {"live": live_label, "change": change_label}

        self.refresh_live_data_only(0)

    def add_custom_coin(self, instance):
        input_coin = self.pair_input.text.strip().upper()
        if not input_coin: return
        if input_coin.endswith("USDT"): input_coin = input_coin.replace("USDT", "")

        target_pair = f"{input_coin}USDT"
        if target_pair in self.fixed_pairs: return

        url = f"https://api.binance.com/api/v3/ticker/price?symbol={target_pair}"
        
        # Async HTTP Request
        UrlRequest(
            url,
            on_success=lambda req, result, coin=input_coin, pair=target_pair: self.on_add_coin_success(result, coin, pair),
            on_error=lambda req, err: None,
            on_failure=lambda req, result: None,
            timeout=5
        )

    def on_add_coin_success(self, result, coin, pair):
        try:
            self.fixed_pairs[pair] = float(result['price'])
            self.known_matrix_coins.add(coin)
            self.rebuild_matrix_dictionary()
            self.pair_input.text = ""
            self.rebuild_ui_layout_structures()
        except:
            pass

    def remove_coin_completely(self, row_key):
        if "USDT" in row_key:
            base_coin = row_key.replace("USDT", "")
            if row_key in self.fixed_pairs: del self.fixed_pairs[row_key]
            if base_coin in self.known_matrix_coins: self.known_matrix_coins.remove(base_coin)
            self.rebuild_matrix_dictionary()
        else:
            if row_key in self.matrix_pairs: del self.matrix_pairs[row_key]

        self.rebuild_ui_layout_structures()

    def on_fixed_price_edit(self, row_key, new_text_value):
        try:
            val = float(new_text_value)
            if self.current_tab == 'tab1':
                self.fixed_pairs[row_key] = val
                self.rebuild_matrix_dictionary()
            else:
                self.matrix_pairs[row_key] = val
        except ValueError:
            pass

    def refresh_live_data_only(self, dt):
        """Fetches live prices asynchronously to prevent blocking the main thread"""
        url = "https://api.binance.com/api/v3/ticker/price"
        UrlRequest(
            url,
            on_success=self.on_prices_fetch_success,
            on_error=lambda req, err: None,
            on_failure=lambda req, result: None,
            timeout=4
        )

    def on_prices_fetch_success(self, req, result):
        try:
            live_prices = {item['symbol']: float(item['price']) for item in result}
        except:
            return

        if self.current_tab == 'tab1':
            for symbol, fixed_price in list(self.fixed_pairs.items()):
                live_price = live_prices.get(symbol)
                if live_price and symbol in self.ui_references:
                    pct = ((live_price - fixed_price) / fixed_price) * 100
                    color = "[color=FF0000]" if pct < 0 else "[color=00FF00]"

                    self.ui_references[symbol]["live"].text = f"{live_price:,.4f}"
                    self.ui_references[symbol]["change"].text = f"{color}{pct:+.2f}%[/color]"

        elif self.current_tab == 'tab2':
            for pair_label, fixed_ratio in list(self.matrix_pairs.items()):
                base, quote = pair_label.split('/')
                base_usdt = live_prices.get(f"{base}USDT")
                quote_usdt = live_prices.get(f"{quote}USDT")

                if base_usdt and quote_usdt and pair_label in self.ui_references:
                    live_ratio = base_usdt / quote_usdt
                    pct = ((live_ratio - fixed_ratio) / fixed_ratio) * 100
                    color = "[color=FF0000]" if pct < 0 else "[color=00FF00]"

                    self.ui_references[pair_label]["live"].text = f"{live_ratio:,.4f}"
                    self.ui_references[pair_label]["change"].text = f"{color}{pct:+.2f}%[/color]"

if __name__ == "__main__":
    CryptoTrackerApp().run()
