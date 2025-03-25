from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QDoubleSpinBox, QMessageBox, QRadioButton, QTextEdit, QDialog
)
from PyQt6.QtCore import QTimer
import winsound
import os
from domain.entities import PriceLimits
from data.api_client import PorssiSahkoApiClient
from datetime import datetime, timezone, timedelta

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Electricity Spot Price Monitor")
        self.setMinimumSize(400, 200)

        self.api_client = PorssiSahkoApiClient()
        self.price_limits = PriceLimits(lower_limit=0.0, upper_limit=10.0)

        self.setup_ui()
        self.setup_timer()
        self.update_prices()  # Call to show prices on startup

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Price display
        price_layout = QHBoxLayout()
        self.current_price_label = QLabel("Current Price: --")
        self.next_price_label = QLabel("Next Hour Price: --")
        price_layout.addWidget(self.current_price_label)
        price_layout.addWidget(self.next_price_label)
        layout.addLayout(price_layout)

        # Price limits
        limits_layout = QHBoxLayout()
        limits_layout.addWidget(QLabel("Lower Limit:"))
        self.lower_limit_spin = QDoubleSpinBox()
        self.lower_limit_spin.setRange(0, 100)
        self.lower_limit_spin.setValue(self.price_limits.lower_limit)
        limits_layout.addWidget(self.lower_limit_spin)

        limits_layout.addWidget(QLabel("Upper Limit:"))
        self.upper_limit_spin = QDoubleSpinBox()
        self.upper_limit_spin.setRange(0, 100)
        self.upper_limit_spin.setValue(self.price_limits.upper_limit)
        limits_layout.addWidget(self.upper_limit_spin)

        layout.addLayout(limits_layout)

        # Notification preferences
        self.lower_price_radio = QRadioButton("Notify for Lower Prices")
        self.lower_price_radio.setChecked(True)  # Default checked
        self.higher_price_radio = QRadioButton("Notify for Higher Prices")
        self.both_prices_radio = QRadioButton("Notify for Both Prices")
        layout.addWidget(self.lower_price_radio)
        layout.addWidget(self.higher_price_radio)
        layout.addWidget(self.both_prices_radio)

        # Update button
        self.update_button = QPushButton("Update Prices")
        self.update_button.clicked.connect(self.update_prices)
        layout.addWidget(self.update_button)

        self.show_daily_prices_button = QPushButton("Show Daily Prices")
        self.show_daily_prices_button.clicked.connect(self.show_daily_prices)
        layout.addWidget(self.show_daily_prices_button)

    def show_daily_prices(self):
        prices = self.api_client.get_daily_prices()
        price_text = "\n\n".join(
            f"{price.start_date.strftime('%Y-%m-%d %H:%M:%S')}: {price.price:.3f} snt/kWh" 
            for price in prices
        )

        # Create a dialog to show the prices
        dialog = QDialog(self)
        dialog.setWindowTitle("Daily Prices")
        dialog.setMinimumSize(300, 200)
        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(price_text)
        layout.addWidget(text_edit)

        dialog.exec()

    def setup_timer(self):
        now = datetime.now(timezone.utc)
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        time_until_next_hour = int((next_hour - now).total_seconds() * 1000)  # Convert to milliseconds and cast to int

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_prices)
        self.timer.start(time_until_next_hour)

    def update_prices(self):
        try:
            current_price, next_price = self.api_client.get_current_and_next_hour_prices()

            current_price_cents = current_price.price
            next_price_cents = next_price.price

            self.current_price_label.setText(f"Current Price: {current_price_cents:.3f} snt/kWh")
            self.next_price_label.setText(f"Next Hour Price: {next_price_cents:.3f} snt/kWh")

            # Update price limits
            self.price_limits = PriceLimits(
                lower_limit=self.lower_limit_spin.value(),
                upper_limit=self.upper_limit_spin.value()
            )

            # Check if prices are within limits and notify accordingly
            notify_lower = self.lower_price_radio.isChecked() or self.both_prices_radio.isChecked()
            notify_higher = self.higher_price_radio.isChecked() or self.both_prices_radio.isChecked()

            if (notify_lower and current_price.price < self.price_limits.lower_limit) or \
               (notify_higher and current_price.price > self.price_limits.upper_limit):
                self.show_notification(current_price.price)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update prices: {str(e)}")

    def show_notification(self, price: float):
        # Determine if the price is lower or higher than the limits
        if price < self.price_limits.lower_limit:
            message = f"Current price ({price:.3f} snt/kWh) is lower than the set lower limit!"
        elif price > self.price_limits.upper_limit:
            message = f"Current price ({price:.3f} snt/kWh) is higher than the set upper limit!"

        # Play notification sound
        try:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        except:
            pass  # Ignore if sound fails

        # Show popup
        QMessageBox.warning(self, "Price Alert", message)