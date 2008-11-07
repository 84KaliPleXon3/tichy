

import time 

import tichy
from tichy import gui

import logging
logger = logging.getLogger('Gadget.GSM')

class GSM(tichy.Gadget):
    """Register on the gsm network and retrieve all the contacts from the sim.
    
    This task also create a label that shows the status of GSM.
    """
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
        sms_service = tichy.Service('SMS')
        gsm_service.connect('provider-modified', on_provider_modified)
        try:
            yield gsm_service.register(on_step)  # start the registration process
        except Exception, e: # Note : That is a little hackish, I should only filter GSM errors
            logger.error("Error: %s", e)
            gsm_status.value = 'GSM Error'
        
        try:
            gsm_status.value = 'Retreive Contacts'
            contacts = yield sim_service.get_contacts() # Get the contacts from the sim
            contacts_service = tichy.Service('Contacts')
            for (name, tel) in contacts:
                contact = contacts_service.create(name, source='sim')
                contact['tel'] = tichy.phone.TelNumber(tel)
        except Exception, e:
            logger.error("Error: %s", e)
            gsm_status.value = 'SIM Error'
        gsm_status.value = gsm_service.get_provider() or "No GSM"
        
            
class NetworkStatus(tichy.Gadget):
    """Monitor the GSM network status.
    
    This will show a little icon representing the strenght of the signal. 
    """
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
        
