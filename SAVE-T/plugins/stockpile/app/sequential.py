import logging
import asyncio
from time import sleep


class LogicalPlanner:

    def __init__(self, operation, planning_svc):
        self.logger = logging.getLogger("sequential")
        self.operation = operation
        self.planning_svc = planning_svc
        self.agent_svc = planning_svc.get_service('agent_svc')
        self.data_svc = planning_svc.get_service('data_svc')

    async def execute(self, phase, hosts):
        operation = (await self.data_svc.explode_operation(dict(id=self.operation['id'])))[0]
        for member in hosts:
            for l in await self.planning_svc.select_links(operation, member, phase):
                l.pop('rewards', [])
                await self.agent_svc.perform_action(l)
        await self.planning_svc.wait_for_phase(operation)
        return 1

    async def find_host_diff(self, previous_hosts, total_phases):
        '''
        :param previous_hosts: the dictionary of hosts that the operation already ran with
        :param total_phases: Just a dummy so it waits till after things finish
        :return:
        '''

        self.logger.debug(f"Total phases done {total_phases}")
        self.logger.debug("Waiting 10 seconds for new agents to check in")

        await asyncio.sleep(10)
        operation = (await self.data_svc.explode_operation(dict(id=self.operation['id'])))[0]

        updated_hosts = operation['host_group']
        ret = []
        if len(updated_hosts) > len(previous_hosts):
            for item1 in updated_hosts:
                found = False
                for item2 in previous_hosts:
                    if item1['id'] == item2['id']:
                        found = True
                        break
                if not found:
                    ret.append(item1)

            return ret
        return None
