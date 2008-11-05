

import time 

import tichy
from tichy import gui

class GSM(tichy.Gadget):
    name = 'GSM'
    def run(self, window):
        # We register into gsm
        gsm_status = tichy.Text('...')
        gsm_status.view(window)
        
        def on_step(msg):
            gsm_status.value = msg
            
        def on_provider_modified(service, provider):
            on_step(provider)
        
        gsm_service = tichy.Service('GSM')
        sim_service = tichy.Service('SIM')
        gsm_service.connect('provider-modified', on_provider_modified)
        try:
            yield gsm_service.register(on_step)  # start the registration process
            gsm_status.value = 'Retreive Contacts'
            contacts = yield sim_service.get_contacts() # Get the contacts from the sim
            contacts_service = tichy.Service('Contacts')
            for (name, tel) in contacts:
                contact = contacts_service.create(name, source='sim')
                contact['tel'] = tichy.phone.TelNumber(tel)
            gsm_status.value = gsm_service.get_provider()
        except: # Note : That is a little hackish, I should only filter GSM errors
            gsm_status.value = 'GSM Error'
            
class NetworkStatus(tichy.Gadget):
    name = 'Network'
    def run(self, window):
        image = tichy.Image(self.path('network0.png'), (32, 32))
        image.view(window)
        
        gsm_service = tichy.Service('GSM')
        
        def on_network_strength(gsm, strength):
            # We assume the strenght can go from 0 to 100 (is it true ?)
            # The images index go from 0 to 4
            index = strength * 4 / 100
            assert index >= 0 and index <= 4
            image.path = self.path('network%d.png' % index)
            
        gsm_service.connect('network-strength', on_network_strength)
        
        yield None
        
