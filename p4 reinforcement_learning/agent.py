import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # Initialize any additional variables here
        self.next_waypoint = None
        self.q_table = Q_table()

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
         # (Total steps, total reward) till now
        self.next_waypoint = None
        self.result = [0, 0]  # (Total steps, total reward) till now

    def update(self, t):

        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        self.eplison = 0.05
        Q_learing = True
        #sense the environment
        self.state = ( ('input', str(inputs)),('next_waypoint',self.next_waypoint))

        # Select action
        if Q_learing:
            if random.random()< self.eplison:
                action = random.choice(Environment.valid_actions) # Select random action
            else:
                action = self.q_table.best_action(self.state)
        else:
            action = random.choice(Environment.valid_actions) # Select random action

        # Execute action and get reward
        reward = self.env.act(self, action)

        # Update state
        new_inputs = self.env.sense(self)
        self.next_waypoint = self.planner.next_waypoint()
        self.new_state = (('input', str(new_inputs)),('next_waypoint',self.next_waypoint))

        #update Q_table using current state, current action, current reward, and next state
        if Q_learing:
            self.q_table.update_Q(self.state,self.new_state,reward,action)

        self.result[0] += 1
        self.result[1] += reward

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}, total reward = {}, total_step = {}".format(deadline, inputs, action, reward, self.result[1],self.result[0])  # [debug]


class Q_table(object):
    def __init__(self):
        self.q = {}
        self.all_actions = [None, 'forward', 'left', 'right']
        self.alpha = 0.7
        self.gamma = 0.7

    def update_Q(self,old_state,new_state,reward,action):
        if new_state not in self.q:
            possible_actions = {possible_action: 0 for possible_action in self.all_actions}
            self.q[new_state] = possible_actions

        self.q[old_state][action] = self.alpha*(reward+self.gamma*(max(self.q[new_state][a] for a in self.all_actions)))+(1-self.alpha)*self.q[old_state][action]

    def best_action(self,state):
        if state not in self.q:
            possible_actions = {possible_action: 0 for possible_action in self.all_actions}
            self.q[state] = possible_actions

        maxq = max(self.q[state][i] for i in self.all_actions)  # [{'forward': 0, 'right': 0, None: 0, 'left': 0}]
        best_acionts = []
        for i in self.all_actions:
            if self.q[state][i] == maxq:
                best_acionts.append(i)
        best_actions = random.choice(best_acionts)

        return best_actions


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=False)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.0,display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':

     run()

