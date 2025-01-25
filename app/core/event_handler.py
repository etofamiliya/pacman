import pygame


class EventHandler:
    def __init__(self, app):
        self.observers = {}
        self.clear = self.observers.clear
        self.app = app

    def add_observer(self, obs, *types):
        for event_type in types:
            if event_type in self.observers:
                self.observers[event_type].append(obs)
            else:
                self.observers[event_type] = [obs]

    def handle(self):
        for event in pygame.event.get():
            for obs in self.observers.get(event.type, []):
                obs.react(self.app, event)
