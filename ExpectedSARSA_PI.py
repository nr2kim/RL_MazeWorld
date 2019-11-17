import numpy as np
import pandas as pd

'''
Initialize Q(s,a), all s in S, a in A(s), arbitrarily, and Q(termina-state, .) = 0
Repeat (for each episode):
    Initialize S
    Choose A from S using policy derived from Q (e.g. epsilon-greedy)
    Repeat (for each step of episode):
        Take action A, observe R, S'
        Q(S, A) <- Q(S, A) + alpha * [R + gamma * sum_a(policy(a|S')*Q(S',a)) - Q(S,A)]
        S <- S', A <- A'
    until S is terminal
'''

class ExpectedSarsa:

    def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.1):
        self.actions = actions  
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)
        self.display_name="ExpectedSARSA"

    '''Choose the next action to take given the observed state using an epsilon greedy policy'''
    def choose_action(self, observation):
        self.check_state_exist(observation)
 
        #BUG: Epsilon should be .1 and signify the small probability of NOT choosing max action
        if np.random.uniform() >= self.epsilon:
            state_action = self.q_table.loc[observation, :]
            action = np.random.choice(state_action[state_action == np.max(state_action)].index)
        else:
            action = np.random.choice(self.actions)
        return action

    def sum_weighted_actions_q(self, observation):
        self.check_state_exist(observation)
        state_action = self.q_table.loc[observation, :]
        best_action = np.random.choice(state_action[state_action == np.max(state_action)].index)
        sum = 0
        for action in self.actions:
            # for each action
            if action == best_action:
                policy = 1-self.epsilon
            else:
                policy = self.epsilon/(len(self.actions) - 1)
            sum += policy * self.q_table.loc[observation, action]
        return sum

    '''Update the Q(S,A) state-action value table using the latest experience
       This is a not a very good learning update 
    '''
    def learn(self, s, a, r, s_):
        self.check_state_exist(s_)
        a_ = self.choose_action(str(s_))
        if s_ != 'terminal':
            q_target = self.q_table.loc[s, a] + self.lr * (r + self.gamma * self.sum_weighted_actions_q(str(s_)) - self.q_table.loc[s, a]); 
        else:
            q_target = self.q_table.loc[s, a] + self.lr * (r + self.q_table.loc[s, a]) # next state is terminal
        self.q_table.loc[s, a] = q_target  # update
        return s_, a_


    '''States are dynamically added to the Q(S,A) table as they are encountered'''
    def check_state_exist(self, state):
        if state not in self.q_table.index:
            # append new state to q table
            self.q_table = self.q_table.append(
                pd.Series(
                    [0]*len(self.actions),
                    index=self.q_table.columns,
                    name=state,
                )
            )