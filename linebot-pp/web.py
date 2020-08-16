from browser import alert
from vue import VueComponent

class HelloVuePy(VueComponent):
    greeting = "Hello vue.py"

    def greet(self, event):
        alert(self.greeting)

    template = """
    <button @click="greet">click me</button>
    """
