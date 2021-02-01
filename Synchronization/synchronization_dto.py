

class SynchronizationDTO():

    def __init__(self, synchronization):
        self.id =synchronization.id
        self.date = synchronization.date
        self.modified = synchronization.get_number_of_modifications()
        self.status = synchronization.status