import sys
import pygame

try:
    from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout
    from PyQt5.QtGui import QPixmap, QPainter, QColor, QImage
    from PyQt5.QtCore import QTimer, Qt, QRect
except ModuleNotFoundError:
    print("Error: PyQt5 is not installed. Please install it using 'pip install PyQt5'")
    sys.exit(1)

class GamepadVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        print("Initializing Gamepad Visualizer UI...")

        pygame.init()
        pygame.joystick.init()

        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Connected to: {self.joystick.get_name()}")
        else:
            print("No game controller detected! Running in UI-only mode.")

        self.setWindowTitle("Gamepad Visualizer")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.canvas = QLabel(self)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gamepad)
        self.timer.start(30)

        self.show()

        self.joysticks = {}

    def resizeEvent(self, event):
        self.repaint()

    def update_gamepad(self):
        # Event processing step.
        # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.JOYBUTTONDOWN:
                # print("Joystick button pressed.")
                if event.button == 0:
                    joystick = self.joysticks[event.instance_id]
                    if joystick.rumble(0, 0.7, 500):
                        print(f"Rumble effect played on joystick {event.instance_id}")

            if event.type == pygame.JOYBUTTONUP:
                # print("Joystick button released.")
                pass

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                joy = pygame.joystick.Joystick(event.device_index)
                self.joysticks[joy.get_instance_id()] = joy
                print(f"Joystick {joy.get_instance_id()} connencted")

            if event.type == pygame.JOYDEVICEREMOVED:
                del self.joysticks[event.instance_id]
                print(f"Joystick {event.instance_id} disconnected")

        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()

        # If there are any joysticks, simply store the first one
        if joystick_count > 0:
            self.joystick = pygame.joystick.Joystick(0)
        else:
            self.joystick = None


        for joystick in self.joysticks.values():
            jid = joystick.get_instance_id()

            # Get the name from the OS for the controller/joystick.
            name = joystick.get_name()
            guid = joystick.get_guid()
            power_level = joystick.get_power_level()

            # Usually axis run in pairs, up/down for one, and left/right for
            # the other. Triggers count as axes.
            axes = joystick.get_numaxes()

            for i in range(axes):
                axis = joystick.get_axis(i)

            buttons = joystick.get_numbuttons()

            for i in range(buttons):
                button = joystick.get_button(i)

            hats = joystick.get_numhats()

            # Hat position. All or nothing for direction, not a float like
            # get_axis(). Position is a tuple of int values (x, y).
            for i in range(hats):
                hat = joystick.get_hat(i)

        QApplication.processEvents()
        self.repaint()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)

        # Draw background
        qp.fillRect(self.rect(), QColor(50, 50, 50))

        # Define base positions relative to the image size
        base_width = 600
        base_height = 400

        # Load and scale controller image
        controller_img = QImage("controller_image.png")
        if not controller_img.isNull():
            scaled_img = controller_img.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_x = (self.width() - scaled_img.width()) // 2
            img_y = (self.height() - scaled_img.height()) // 2
            qp.drawImage(QRect(img_x, img_y, scaled_img.width(), scaled_img.height()), scaled_img)

        if not self.joystick:
            qp.setPen(QColor(255, 255, 255))
            qp.drawText(self.rect(), Qt.AlignCenter, "No gamepad detected")
            qp.end()
            return

        scale_x = scaled_img.width() / base_width
        scale_y = scaled_img.height() / base_height
        img_x_offset = img_x
        img_y_offset = img_y

        # compute the circle scaling factor (e.g. the scale factor which
        # maintains square aspect ratio for a circle or square)
        scale_x = min(scale_x, scale_y)
        scale_y = scale_x

        def draw_element(x, y, w, h, color, shape="ellipse"):
            qp.setBrush(color)
            pos_x = int(img_x_offset + x * scale_x)
            pos_y = int(img_y_offset + y * scale_y)
            width = int(w * scale_x)
            height = int(h * scale_y)
            if shape == "ellipse":
                qp.drawEllipse(pos_x, pos_y, width, height)
            else:
                qp.drawRect(pos_x, pos_y, width, height)

        joystick_positions = {
            "left": (115, 210, 30, 30),
            "right": (365, 295, 30, 30)
        }

        trigger_positions = {
            "left": (120, 20, 50, 60),
            "right": (440, 20, 50, 60)
        }

        bumper_positions = {
            "l1": (120, 120, 50, 20),
            "r1": (440, 120, 50, 20)
        }

        button_positions = {
            0: (445, 250, 30, 30),  # A
            1: (485, 210, 30, 30),  # B
            2: (405, 210, 30, 30),  # X
            3: (445, 170, 30, 30)   # Y
        }

        dpad_positions = {
            "up": (195, 270, 25, 25),
            "down": (195, 320, 25, 25),
            "left": (170, 295, 25, 25),
            "right": (220, 295, 25, 25)
        }

        for joystick, (x, y, w, h) in joystick_positions.items():
            index = 0 if joystick == "left" else 3
            pos_x = x + int(self.joystick.get_axis(index) * 20)
            pos_y = y + int(self.joystick.get_axis(index + 1) * 20)
            # set the color based on whether or not the L3 or R3 button is pressed
            if joystick == "left":
                color = QColor(0, 255, 0) if self.joystick.get_button(6) else QColor(127, 127, 127)
            else:
                color = QColor(0, 255, 0) if self.joystick.get_button(7) else QColor(127, 127, 127)
            draw_element(pos_x, pos_y, w, h, color)

        for trigger, (x, y, w, h) in trigger_positions.items():
            index = 2 if trigger == "left" else 5
            # clamp axis value to be [0,1]
            value = max(0, min(1, self.joystick.get_axis(index)))
            height = int(value * h)
            draw_element(x, y, w, h, QColor(127, 127, 127), shape="rect")
            draw_element(x, y + (h-height), w, height, QColor(0, 255, 0), shape="rect")

        for button, (x, y, w, h) in button_positions.items():
            color = QColor(0, 255, 0) if self.joystick.get_button(button) else QColor(100, 100, 100)
            draw_element(x, y, w, h, color)

        for direction, (x, y, w, h) in dpad_positions.items():
            active = False
            hat = self.joystick.get_hat(0)
            if direction == "up" and hat[1] == 1:
                active = True
            elif direction == "down" and hat[1] == -1:
                active = True
            elif direction == "left" and hat[0] == -1:
                active = True
            elif direction == "right" and hat[0] == 1:
                active = True

            color = QColor(0, 255, 0) if active else QColor(100, 100, 100)
            draw_element(x, y, w, h, color, shape="rect")

        for bumper, (x, y, w, h) in bumper_positions.items():
            color = QColor(0, 255, 0) if self.joystick.get_button(4 if bumper == "l1" else 5) else QColor(100, 100, 100)
            draw_element(x, y, w, h, color, shape="rect")

        qp.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GamepadVisualizer()
    sys.exit(app.exec_())
