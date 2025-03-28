"""
Main window implementation for the Electricity Spot Price Monitor application.
This module provides the GUI interface for monitoring electricity spot prices,
setting price limits, and receiving notifications.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QDoubleSpinBox, QMessageBox, QRadioButton, QTextEdit, QDialog,
    QComboBox, QFrame, QSizeGrip
)
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QPalette, QColor, QFont, QIcon
import winsound
import os
from domain.entities import PriceLimits
from data.api_client import PorssiSahkoApiClient
from datetime import datetime, timezone, timedelta

class TitleBar(QFrame):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.parent = parent
        self.theme = theme
        self.setup_ui()
        self.start = QPoint(0, 0)
        self.pressing = False

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Title
        title = QLabel("Electricity Spot Price Monitor")
        title.setStyleSheet(f"color: {self.theme['primary']}; font-weight: bold;")
        layout.addWidget(title)

        # Window controls
        controls = QHBoxLayout()
        controls.setSpacing(5)

        # Minimize button
        min_button = QPushButton("─")
        min_button.setFixedSize(20, 20)
        min_button.clicked.connect(self.parent.showMinimized)
        min_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['background']};
                color: {self.theme['primary']};
                border: 1px solid {self.theme['primary']};
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['primary']};
                color: {self.theme['background']};
            }}
        """)

        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(self.parent.close)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['background']};
                color: {self.theme['primary']};
                border: 1px solid {self.theme['primary']};
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['primary']};
                color: {self.theme['background']};
            }}
        """)

        controls.addWidget(min_button)
        controls.addWidget(close_button)
        layout.addLayout(controls)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme['background']};
                border-bottom: 1px solid {self.theme['primary']};
            }}
        """)

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end - self.start
            self.parent.setGeometry(self.mapToGlobal(self.movement).x(),
                                  self.mapToGlobal(self.movement).y(),
                                  self.parent.width(),
                                  self.parent.height())
            self.start = self.end

    def mouseReleaseEvent(self, event):
        self.pressing = False

class StyledDialog(QDialog):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.theme = theme
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()
        
        # Center the dialog on the parent window
        if parent:
            parent_geometry = parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
            # Ensure the dialog is raised to the top
            self.raise_()
            self.activateWindow()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Container
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme['background']};
                border-radius: 10px;
                border: 2px solid {self.theme['primary']};
            }}
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)

        # Title bar
        title_bar = TitleBar(self, self.theme)
        container_layout.addWidget(title_bar)

        # Content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 10, 0, 0)
        container_layout.addWidget(content)

        # Add size grip
        size_grip = QSizeGrip(self)
        size_grip.setStyleSheet(f"""
            QSizeGrip {{
                background-color: {self.theme['background']};
                color: {self.theme['primary']};
            }}
        """)
        container_layout.addWidget(size_grip, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        layout.addWidget(container)
        self.content_layout = content_layout

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
        self.setMinimumSize(600, 400)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.api_client = PorssiSahkoApiClient()
        self.price_limits = PriceLimits(lower_limit=0.0, upper_limit=10.0)
        
        # Theme colors
        self.themes = {
            "Neon Green": {"primary": "#00ff00", "secondary": "#00cc00", "background": "rgba(0, 0, 0, 180)"},
            "Cyber Blue": {"primary": "#00ffff", "secondary": "#0099ff", "background": "rgba(0, 0, 0, 180)"},
            "Purple Haze": {"primary": "#ff00ff", "secondary": "#cc00cc", "background": "rgba(0, 0, 0, 180)"},
            "Sunset": {"primary": "#ff6600", "secondary": "#ff3300", "background": "rgba(0, 0, 0, 180)"}
        }
        self.current_theme = "Neon Green"

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
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title bar
        self.title_bar = TitleBar(self, self.themes[self.current_theme])
        layout.addWidget(self.title_bar)

        # Main container
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {self.themes[self.current_theme]["background"]};
                border-radius: 0 0 15px 15px;
                border: 2px solid {self.themes[self.current_theme]["primary"]};
                border-top: none;
            }}
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(20, 20, 20, 20)

        # Settings row
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("Theme:"))
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(self.themes.keys())
        self.theme_selector.setCurrentText(self.current_theme)
        self.theme_selector.currentTextChanged.connect(self.change_theme)
        settings_layout.addWidget(self.theme_selector)
        container_layout.addLayout(settings_layout)

        # Price display
        price_layout = QHBoxLayout()
        price_layout.setSpacing(30)
        
        # Current price
        current_price_container = QFrame()
        current_price_container.setStyleSheet(f"""
            QFrame {{
                background-color: {self.themes[self.current_theme]["background"]};
                border-radius: 10px;
                border: 2px solid {self.themes[self.current_theme]["primary"]};
            }}
        """)
        current_price_layout = QVBoxLayout(current_price_container)
        current_price_label = QLabel("Current Price")
        current_price_label.setStyleSheet(f"color: {self.themes[self.current_theme]['primary']}; font-size: 16px;")
        self.current_price_label = QLabel("--")
        self.current_price_label.setStyleSheet(f"color: {self.themes[self.current_theme]['primary']}; font-size: 48px; font-weight: bold;")
        current_price_layout.addWidget(current_price_label)
        current_price_layout.addWidget(self.current_price_label)
        
        # Next price
        next_price_container = QFrame()
        next_price_container.setStyleSheet(f"""
            QFrame {{
                background-color: {self.themes[self.current_theme]["background"]};
                border-radius: 10px;
                border: 2px solid {self.themes[self.current_theme]["primary"]};
            }}
        """)
        next_price_layout = QVBoxLayout(next_price_container)
        next_price_label = QLabel("Next Hour Price")
        next_price_label.setStyleSheet(f"color: {self.themes[self.current_theme]['primary']}; font-size: 16px;")
        self.next_price_label = QLabel("--")
        self.next_price_label.setStyleSheet(f"color: {self.themes[self.current_theme]['primary']}; font-size: 32px; font-weight: bold;")
        next_price_layout.addWidget(next_price_label)
        next_price_layout.addWidget(self.next_price_label)
        
        price_layout.addWidget(current_price_container)
        price_layout.addWidget(next_price_container)
        container_layout.addLayout(price_layout)

        # Price limits
        limits_layout = QHBoxLayout()
        limits_layout.setSpacing(20)
        
        # Lower limit
        lower_limit_container = QFrame()
        lower_limit_container.setStyleSheet(f"""
            QFrame {{
                background-color: {self.themes[self.current_theme]["background"]};
                border-radius: 10px;
                border: 2px solid {self.themes[self.current_theme]["primary"]};
            }}
        """)
        lower_limit_layout = QVBoxLayout(lower_limit_container)
        lower_limit_label = QLabel("Lower Limit")
        lower_limit_label.setStyleSheet(f"color: {self.themes[self.current_theme]['primary']};")
        self.lower_limit_spin = QDoubleSpinBox()
        self.lower_limit_spin.setRange(0, 100)
        self.lower_limit_spin.setValue(self.price_limits.lower_limit)
        self.lower_limit_spin.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {self.themes[self.current_theme]["background"]};
                color: {self.themes[self.current_theme]["primary"]};
                border: 1px solid {self.themes[self.current_theme]["primary"]};
                border-radius: 5px;
                padding: 5px;
            }}
        """)
        lower_limit_layout.addWidget(lower_limit_label)
        lower_limit_layout.addWidget(self.lower_limit_spin)
        
        # Upper limit
        upper_limit_container = QFrame()
        upper_limit_container.setStyleSheet(f"""
            QFrame {{
                background-color: {self.themes[self.current_theme]["background"]};
                border-radius: 10px;
                border: 2px solid {self.themes[self.current_theme]["primary"]};
            }}
        """)
        upper_limit_layout = QVBoxLayout(upper_limit_container)
        upper_limit_label = QLabel("Upper Limit")
        upper_limit_label.setStyleSheet(f"color: {self.themes[self.current_theme]['primary']};")
        self.upper_limit_spin = QDoubleSpinBox()
        self.upper_limit_spin.setRange(0, 100)
        self.upper_limit_spin.setValue(self.price_limits.upper_limit)
        self.upper_limit_spin.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {self.themes[self.current_theme]["background"]};
                color: {self.themes[self.current_theme]["primary"]};
                border: 1px solid {self.themes[self.current_theme]["primary"]};
                border-radius: 5px;
                padding: 5px;
            }}
        """)
        upper_limit_layout.addWidget(upper_limit_label)
        upper_limit_layout.addWidget(self.upper_limit_spin)
        
        limits_layout.addWidget(lower_limit_container)
        limits_layout.addWidget(upper_limit_container)
        container_layout.addLayout(limits_layout)

        # Notification preferences
        notification_container = QFrame()
        notification_container.setStyleSheet(f"""
            QFrame {{
                background-color: {self.themes[self.current_theme]["background"]};
                border-radius: 10px;
                border: 2px solid {self.themes[self.current_theme]["primary"]};
            }}
        """)
        notification_layout = QVBoxLayout(notification_container)
        notification_label = QLabel("Notification Preferences")
        notification_label.setStyleSheet(f"color: {self.themes[self.current_theme]['primary']}; font-size: 16px;")
        notification_layout.addWidget(notification_label)
        
        self.lower_price_radio = QRadioButton("Notify for Lower Prices")
        self.higher_price_radio = QRadioButton("Notify for Higher Prices")
        self.both_prices_radio = QRadioButton("Notify for Both Prices")
        
        for radio in [self.lower_price_radio, self.higher_price_radio, self.both_prices_radio]:
            radio.setStyleSheet(f"color: {self.themes[self.current_theme]['primary']};")
            notification_layout.addWidget(radio)
        
        self.lower_price_radio.setChecked(True)
        container_layout.addWidget(notification_container)

        # Buttons
        button_container = QFrame()
        button_container.setStyleSheet(f"""
            QFrame {{
                background-color: {self.themes[self.current_theme]["background"]};
                border-radius: 10px;
                border: 2px solid {self.themes[self.current_theme]["primary"]};
            }}
        """)
        button_layout = QHBoxLayout(button_container)
        
        self.update_button = QPushButton("Update Prices")
        self.show_daily_prices_button = QPushButton("Show Daily Prices")
        self.show_next_day_prices_button = QPushButton("Show Next Day Prices")
        
        for button in [self.update_button, self.show_daily_prices_button, self.show_next_day_prices_button]:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.themes[self.current_theme]["background"]};
                    color: {self.themes[self.current_theme]["primary"]};
                    border: 2px solid {self.themes[self.current_theme]["primary"]};
                    border-radius: 5px;
                    padding: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.themes[self.current_theme]["primary"]};
                    color: {self.themes[self.current_theme]["background"]};
                }}
            """)
            button_layout.addWidget(button)
        
        self.update_button.clicked.connect(self.update_prices)
        self.show_daily_prices_button.clicked.connect(self.show_daily_prices)
        self.show_next_day_prices_button.clicked.connect(self.show_next_day_prices)
        
        container_layout.addWidget(button_container)

        # Add size grip for resizing
        size_grip = QSizeGrip(self)
        size_grip.setFixedSize(20, 20)  # Fixed size for better visibility
        size_grip.setStyleSheet(f"""
            QSizeGrip {{
                background-color: {self.themes[self.current_theme]["background"]};
                color: {self.themes[self.current_theme]["primary"]};
            }}
        """)
        container_layout.addWidget(size_grip, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        layout.addWidget(container)

    def change_theme(self, theme_name):
        """
        Change the application theme colors.
        
        Args:
            theme_name (str): Name of the selected theme
        """
        self.current_theme = theme_name
        self.setup_ui()  # Rebuild UI with new theme
        self.update_prices()  # Update prices to apply new styling

    def show_daily_prices(self):
        """
        Display a dialog showing the daily electricity prices.
        Fetches prices from the API and formats them for display.
        """
        try:
            print("Fetching daily prices...")  # Debug log
            prices = self.api_client.get_daily_prices()
            print(f"Got {len(prices)} prices")  # Debug log
            
            now = datetime.now(timezone.utc)
            start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_today = start_of_today + timedelta(days=1) - timedelta(microseconds=1)

            # Filter prices for today
            today_prices = [
                price for price in prices
                if start_of_today <= price.start_date <= end_of_today
            ]
            print(f"Filtered to {len(today_prices)} prices for today")  # Debug log

            if not today_prices:
                print("No prices available for today")  # Debug log
                msg = QMessageBox(self)
                msg.setWindowTitle("Daily Prices")
                msg.setText("No prices available for today.")
                msg.setStyleSheet(f"""
                    QMessageBox {{
                        background-color: {self.themes[self.current_theme]["background"]};
                    }}
                    QMessageBox QLabel {{
                        color: {self.themes[self.current_theme]["primary"]};
                    }}
                    QPushButton {{
                        background-color: {self.themes[self.current_theme]["background"]};
                        color: {self.themes[self.current_theme]["primary"]};
                        border: 1px solid {self.themes[self.current_theme]["primary"]};
                        border-radius: 5px;
                        padding: 5px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.themes[self.current_theme]["primary"]};
                        color: {self.themes[self.current_theme]["background"]};
                    }}
                """)
                msg.exec()
                return

            price_text = "\n\n".join(
                f"{price.start_date.strftime('%Y-%m-%d %H:%M:%S')}: {price.price:.3f} snt/kWh" 
                for price in today_prices
            )
            print("Created price text")  # Debug log

            dialog = StyledDialog(self, self.themes[self.current_theme])
            dialog.setMinimumSize(400, 300)
            
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setText(price_text)
            text_edit.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {self.themes[self.current_theme]["background"]};
                    color: {self.themes[self.current_theme]["primary"]};
                    border: 1px solid {self.themes[self.current_theme]["primary"]};
                    border-radius: 5px;
                    padding: 5px;
                }}
            """)
            dialog.content_layout.addWidget(text_edit)

            print("Showing dialog...")  # Debug log
            dialog.exec()
            print("Dialog closed")  # Debug log

        except Exception as e:
            print(f"Error in show_daily_prices: {str(e)}")  # Debug log
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Failed to fetch daily prices: {str(e)}")
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {self.themes[self.current_theme]["background"]};
                }}
                QMessageBox QLabel {{
                    color: {self.themes[self.current_theme]["primary"]};
                }}
                QPushButton {{
                    background-color: {self.themes[self.current_theme]["background"]};
                    color: {self.themes[self.current_theme]["primary"]};
                    border: 1px solid {self.themes[self.current_theme]["primary"]};
                    border-radius: 5px;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    background-color: {self.themes[self.current_theme]["primary"]};
                    color: {self.themes[self.current_theme]["background"]};
                }}
            """)
            msg.exec()

    def show_next_day_prices(self):
        """
        Display a dialog showing the next day's electricity prices.
        Shows a message if prices are not available yet.
        """
        try:
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
                msg = QMessageBox(self)
                msg.setWindowTitle("Next Day Prices")
                msg.setText("Prices for next day are not available yet.")
                msg.setStyleSheet(f"""
                    QMessageBox {{
                        background-color: {self.themes[self.current_theme]["background"]};
                    }}
                    QMessageBox QLabel {{
                        color: {self.themes[self.current_theme]["primary"]};
                    }}
                    QPushButton {{
                        background-color: {self.themes[self.current_theme]["background"]};
                        color: {self.themes[self.current_theme]["primary"]};
                        border: 1px solid {self.themes[self.current_theme]["primary"]};
                        border-radius: 5px;
                        padding: 5px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.themes[self.current_theme]["primary"]};
                        color: {self.themes[self.current_theme]["background"]};
                    }}
                """)
                msg.exec()
                return

            price_text = "\n\n".join(
                f"{price.start_date.strftime('%Y-%m-%d %H:%M:%S')}: {price.price:.3f} snt/kWh" 
                for price in tomorrow_prices
            )

            dialog = StyledDialog(self, self.themes[self.current_theme])
            dialog.setMinimumSize(400, 300)
            
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setText(price_text)
            text_edit.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {self.themes[self.current_theme]["background"]};
                    color: {self.themes[self.current_theme]["primary"]};
                    border: 1px solid {self.themes[self.current_theme]["primary"]};
                    border-radius: 5px;
                    padding: 5px;
                }}
            """)
            dialog.content_layout.addWidget(text_edit)

            dialog.exec()
        except Exception as e:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Failed to fetch next day prices: {str(e)}")
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {self.themes[self.current_theme]["background"]};
                }}
                QMessageBox QLabel {{
                    color: {self.themes[self.current_theme]["primary"]};
                }}
                QPushButton {{
                    background-color: {self.themes[self.current_theme]["background"]};
                    color: {self.themes[self.current_theme]["primary"]};
                    border: 1px solid {self.themes[self.current_theme]["primary"]};
                    border-radius: 5px;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    background-color: {self.themes[self.current_theme]["primary"]};
                    color: {self.themes[self.current_theme]["background"]};
                }}
            """)
            msg.exec()

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

        # Show themed popup
        msg = QMessageBox(self)
        msg.setWindowTitle("Price Alert")
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {self.themes[self.current_theme]["background"]};
            }}
            QMessageBox QLabel {{
                color: {self.themes[self.current_theme]["primary"]};
            }}
            QPushButton {{
                background-color: {self.themes[self.current_theme]["background"]};
                color: {self.themes[self.current_theme]["primary"]};
                border: 1px solid {self.themes[self.current_theme]["primary"]};
                border-radius: 5px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {self.themes[self.current_theme]["primary"]};
                color: {self.themes[self.current_theme]["background"]};
            }}
        """)
        msg.exec()