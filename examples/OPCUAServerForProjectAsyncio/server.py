import asyncio
import logging
import random
from asyncua import Server


async def main():
    _logger = logging.getLogger('asyncua')
    server = Server()
    await server.init()
    server.disable_clock() #for debugging
    
    # server.set_endpoint("opc.tcp://PERSONAL_IP_ADDRESS:4840") 
    server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/") #OPC UA Server for test
    server.set_server_name("OPCUA_SIMULATION_SERVER")
    
    # setup our own namespace, not really necessary but should as spec
    uri = 'http://examples.freeopcua.github.io'
    idx = await server.register_namespace(uri)

    # populating our address space
    myobj = await server.nodes.objects.add_object(idx, 'MyObject')
    myvar = await myobj.add_variable(idx, 'MyVariable', [False,False,False,False,False,False,False,False,False,False])

    async def make_new_val(myvar):
        new_val = [] # Initialize
        for i in range(10): #Change Doors state
            new_val.insert(i, bool(random.getrandbits(1)))
        await myvar.write_value(new_val)
        return new_val
    
    async def print_new_val(myvar):
        val = await make_new_val(myvar)
        print ('Set values to :', val)
        return val

    
    #set MyVariable to be writable by clients
    await myvar.set_writable()
    _logger.info('Starting server!')
    print('Starting server!')
        
    async with server:
        while True:
            await print_new_val(myvar)
            await asyncio.sleep(60)
            ''' # run without subroutine
            new_val = [] # Initialize
            for i in range(10): #Change Doors state
                new_val.insert(i, bool(random.getrandbits(1)))
            _logger.info('Set values to ', myvar)
            print('Set values to :', new_val)
            await myvar.write_value(new_val) '''
            

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(), debug=True)
    # run main() with asyncio 
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main()) 