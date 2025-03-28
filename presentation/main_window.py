"""
Main window implementation for the Electricity Spot Price Monitor application.
This module provides the GUI interface for monitoring electricity spot prices,
setting price limits, and receiving notifications.
"""

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
    """
    Main window class that handles the GUI and price monitoring functionality.
    Provides interface for viewing current and next hour prices, setting price limits,
    and configuring notifications.
    """

    def __init__(self):
        """
        Initialize the main window with default settings and UI components.
        Sets up the API client, price limits, and starts the price update timer.
        """
        super().__init__()
        self.setWindowTitle("Electricity Spot Price Monitor")
        self.setMinimumSize(400, 200)

        self.api_client = PorssiSahkoApiClient()
        self.price_limits = PriceLimits(lower_limit=0.0, upper_limit=10.0)

        self.setup_ui()
        self.setup_timer()
        self.update_prices()  # Call to show prices on startup

    def setup_ui(self):
        """
        Set up the user interface components including price displays,
        limit controls, notification preferences, and action buttons.
        """
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

        self.show_next_day_prices_button = QPushButton("Show Next Day Prices")
        self.show_next_day_prices_button.clicked.connect(self.show_next_day_prices)
        layout.addWidget(self.show_next_day_prices_button)

    def show_daily_prices(self):
        """
        Display a dialog showing the daily electricity prices.
        Fetches prices from the API and formats them for display.
        """
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

    def show_next_day_prices(self):
        """
        Display a dialog showing the next day's electricity prices.
        Shows a message if prices are not available yet.
        """
        prices = self.api_client.get_daily_prices()
        now = datetime.now(timezone.utc)
        start_of_tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end_of_tomorrow = start_of_tomorrow + timedelta(days=1) - timedelta(microseconds=1)

        # Filter prices for tomorrow
        tomorrow_prices = [
            price for price in prices
            if start_of_tomorrow <= price.start_date <= end_of_tomorrow
        ]

        if not tomorrow_prices:
            QMessageBox.information(self, "Next Day Prices", "Prices for next day are not available yet.")
            return

        price_text = "\n\n".join(
            f"{price.start_date.strftime('%Y-%m-%d %H:%M:%S')}: {price.price:.3f} snt/kWh" 
            for price in tomorrow_prices
        )

        # Create a dialog to show the prices
        dialog = QDialog(self)
        dialog.setWindowTitle("Next Day Prices")
        dialog.setMinimumSize(300, 200)
        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(price_text)
        layout.addWidget(text_edit)

        dialog.exec()

    def setup_timer(self):
        """
        Set up a timer to update prices at the start of each hour.
        Calculates the time until the next hour and starts the timer.
        """
        now = datetime.now(timezone.utc)
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        time_until_next_hour = int((next_hour - now).total_seconds() * 1000)  # Convert to milliseconds and cast to int

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_prices)
        self.timer.start(time_until_next_hour)

    def update_prices(self):
        """
        Update the displayed prices and check if notifications are needed.
        Fetches current and next hour prices from the API and updates the UI.
        Triggers notifications if prices are outside the set limits.
        """
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
        """
        Show a notification when prices are outside the set limits.
        Plays a system sound and displays a message box with the price alert.

        Args:
            price (float): The current electricity price that triggered the notification
        """
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