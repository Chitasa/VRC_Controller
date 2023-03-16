from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server, udp_client
from .singletons import bus
from threading import Thread


class BotController:
    def __init__(self, name: str = "bot", client: tuple[str, int] = ("127.0.0.1", 9000),
                 server: tuple[str, int] = ("127.0.0.1", 9001)):
        self.name: str = name
        self.client: udp_client.SimpleUDPClient = udp_client.SimpleUDPClient(*client)

        dispatcher = Dispatcher()
        dispatcher.map("/avatar/parameters/*", self._avatar_parameters)
        self.server: osc_server.ThreadingOSCUDPServer = osc_server.ThreadingOSCUDPServer(server, dispatcher)
        Thread(target=self.server.serve_forever, daemon=True).start()

    def _avatar_parameters(self, path, value):
        """
        Dispatches avatar events to the bus, contains `name` for which controller sent the event
        """
        event = path.split("/")[-1]
        bus.emit(event, self.name, value)

    def _send(self, address, data):
        """
        Sends osc message
        """
        self.client.send_message(address, data)

    # Find more here: https://docs.vrchat.com/docs/osc-as-input-controller#supported-inputs
    # These are all untested :)
    def move_forwards(self):
        self._send("/input/Vertical", 1)

    def move_backwards(self):
        self._send("/input/Vertical", -1)

    def move_left(self):
        self._send("/input/Horizontal", -1)

    def move_right(self):
        self._send("/input/Horizontal", 1)

    def look_horizontal(self, amp):
        self._send("/input/LookHorizontal", amp)

    def use_axis(self):
        self._send("/input/UseAxisRight", 1)

    def grab_axis(self):
        self._send("/input/GrabAxisRight", 1)

    def move_hold_forwards(self):
        self._send("/input/MoveHoldFB", 1)

    def move_hold_backwards(self):
        self._send("/input/MoveHoldFB", -1)

    def spin_hold_cw(self):
        self._send("/input/SpinHoldCwCcw", 1)

    def spin_hold_ccw(self):
        self._send("/input/SpinHoldCwCcw", -1)

    def spin_hold_up(self):
        self._send("/input/SpinHoldUD", 1)

    def spin_hold_down(self):
        self._send("/input/SpinHoldUD", -1)

    def spin_hold_left(self):
        self._send("/input/SpinHoldLR", -1)

    def spin_hold_right(self):
        self._send("/input/SpinHoldLR", 1)

    # Button Inputs
    def button_forward(self, on=True):
        self._send("/input/MoveForward", int(on))

    def button_backward(self, on=True):
        self._send("/input/MoveBackward", int(on))

    def button_left(self, on=True):
        self._send("/input/MoveLeft", int(on))

    def button_right(self, on=True):
        self._send("/input/MoveRight", int(on))

    def button_look_left(self, on=True):
        self._send("/input/LookLeft", int(on))

    def button_look_right(self, on=True):
        self._send("/input/LookRight", int(on))

    def button_jump(self, on=True):
        self._send("/input/Jump", int(on))

    def button_run(self, on=True):
        self._send("/input/Run", int(on))

    # VR Only
    def button_comfort_left(self, on=True):
        self._send("/input/ComfortLeft", int(on))

    def button_drop_left(self, on=True):
        self._send("/input/DropLeft", int(on))

    def button_use_left(self, on=True):
        self._send("/input/UseLeft", int(on))

    def button_grab_left(self, on=True):
        self._send("/input/GrabLeft", int(on))

    def button_comfort_right(self, on=True):
        self._send("/input/ComfortRight", int(on))

    def button_drop_right(self, on=True):
        self._send("/input/DropRight", int(on))

    def button_use_right(self, on=True):
        self._send("/input/UseRight", int(on))

    def button_grab_right(self, on=True):
        self._send("/input/GrabRight", int(on))

    # Misc
    def panic_button(self):
        self._send("/input/PanicButton", 1)

    def toggle_quick_menu(self, left=True):
        self._send(f"/input/QuickMenuToggle{['Right', 'Left'][left]}", 1)

    # TODO - make this better
    def toggle_voice(self, on=True):
        self._send("/input/Voice", int(on))

    # Chat box
    def send_message(self, message, open_chatbox=False):
        self._send("/chatbox/input", [message, not open_chatbox])

    def typing(self, on=True):
        self._send("/chatbox/typing", int(on))
