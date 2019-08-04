import math
import os
import sys

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from dots.interpreter import AsciiDotsInterpreter
from dots.environment import Env
from pathlib import Path
from dots.callbacks import IOCallbacksStorageConstructor

FILE_NAME = "agent.dots"

class AsciiAgent(BaseAgent):
	
	# Gets the side we are on as a 0 or 1
	def get_side(self):
		return -1 if self.team == 1 else 1
	
	# Allows for inverting the team if the math doesn't work out
	def get_team(self):
		return self.team
	
	def create_inputs(self, num_cars):
		for i in range(len(self.game_packet), (num_cars-1)*20+100, 1):
			self.game_packet.append(0)
	
	def parse(self, packet: GameTickPacket, inputs):
		side = self.get_side()
		team = self.get_team()
		
		# Ball
		game_ball = packet.game_ball.physics
		inputs[0] = game_ball.location.x * side
		inputs[1] = game_ball.location.y * side
		inputs[2] = game_ball.location.z
		inputs[3] = game_ball.velocity.x * side
		inputs[4] = game_ball.velocity.y * side
		inputs[5] = game_ball.velocity.z
		inputs[6] = game_ball.angular_velocity.x * side
		inputs[7] = game_ball.angular_velocity.y * side
		inputs[8] = game_ball.angular_velocity.z
		inputs[9] = packet.game_ball.drop_shot_info.damage_index
		
		# Agent
		agent_car = packet.game_cars[self.index]
		agent_car_phys = agent_car.physics
		inputs[10] = agent_car_phys.location.x * side
		inputs[11] = agent_car_phys.location.y * side
		inputs[12] = agent_car_phys.location.z
		inputs[13] = agent_car_phys.velocity.x * side
		inputs[14] = agent_car_phys.velocity.y * side
		inputs[15] = agent_car_phys.velocity.z
		inputs[16] = (agent_car_phys.rotation.yaw / math.pi * 180 + 180 * team) % 360
		inputs[17] = agent_car_phys.rotation.pitch / math.pi * 180
		inputs[18] = agent_car_phys.rotation.roll / math.pi * 180
		inputs[19] = agent_car_phys.angular_velocity.x * side
		inputs[20] = agent_car_phys.angular_velocity.y * side
		inputs[21] = agent_car_phys.angular_velocity.z
		
		inputs[22] = agent_car.is_super_sonic
		inputs[23] = agent_car.jumped
		inputs[24] = agent_car.double_jumped
		inputs[25] = agent_car.boost
		inputs[26] = agent_car.is_demolished
		inputs[27] = agent_car.has_wheel_contact
		
		# Game info
		game_info = packet.game_info
		inputs[30] = game_info.seconds_elapsed
		inputs[31] = game_info.game_time_remaining
		inputs[32] = game_info.is_unlimited_time
		inputs[33] = game_info.is_kickoff_pause
		inputs[34] = game_info.is_round_active
		inputs[35] = game_info.world_gravity_z
		inputs[36] = game_info.is_overtime
		inputs[37] = game_info.is_match_ended
		
		# Latest touch
		lt = packet.game_ball.latest_touch
		inputs[40] = lt.hit_location.x
		inputs[41] = lt.hit_location.y
		inputs[42] = lt.hit_location.z
		inputs[43] = lt.hit_normal.x
		inputs[44] = lt.hit_normal.y
		inputs[45] = lt.hit_normal.z
		inputs[47] = lt.team
		inputs[48] = lt.time_seconds
		
		# Other cars in the game
		inputs[99] = packet.num_cars
		latest_touch_name = lt.player_name
		cars = packet.game_cars
		for n in range(packet.num_cars):
			car = cars[n]
			if n != self.index:
				i = n if n < self.index else n - 1
				car_phys = car.physics
				inputs[100+i*20] = car_phys.location.x * side
				inputs[101+i*20] = car_phys.location.y * side
				inputs[102+i*20] = car_phys.location.z
				inputs[103+i*20] = car_phys.velocity.x * side
				inputs[104+i*20] = car_phys.velocity.y * side
				inputs[105+i*20] = car_phys.velocity.z
				inputs[106+i*20] = (car_phys.rotation.yaw / math.pi * 180 + 180 * team) % 360
				inputs[107+i*20] = car_phys.rotation.pitch / math.pi * 180
				inputs[108+i*20] = car_phys.rotation.roll / math.pi * 180
				inputs[109+i*20] = car_phys.angular_velocity.x * side
				inputs[110+i*20] = car_phys.angular_velocity.y * side
				inputs[111+i*20] = car_phys.angular_velocity.z
				
				inputs[112+i*20] = car.is_super_sonic
				
				inputs[116+i*20] = car.is_demolished
				inputs[117+i*20] = car.has_wheel_contact
				
				if car.name == latest_touch_name:
					inputs[46] = i
				
			elif self.name == latest_touch_name:
				inputs[46] = -1
		
		return inputs
		
	
	def get(self, data):
		c = SimpleControllerState()
		c.throttle = max(min(data[0], 1), -1)
		c.steer = max(min(data[1], 1), -1)
		c.pitch = max(min(data[2], 1), -1)
		c.yaw = max(min(data[3], 1), -1)
		c.roll = max(min(data[4], 1), -1)
		c.jump = data[5]
		c.boost = data[6]
		c.handbrake = data[7]
		c.use_item = data[8]
		return c
	
	def initialize_agent(self):
		
		self.interpreter = None
		
		cwd = os.getcwd()
		
		path = os.path.dirname(os.path.realpath(__file__))
		
		os.chdir(path)
		
		env = Env()
		env.io = IOCallbacksStorageConstructor(get_input, on_output, on_finish, on_error, on_microtick)
		env.io.env = env
		
		program_dir = os.path.dirname(os.path.realpath(FILE_NAME))
		with open(FILE_NAME, encoding='utf-8') as file:
			program = file.read()
		
		self.interpreter = AsciiDotsInterpreter(env, program, program_dir, True)
		
		self.p_time = 0
		
		self.game_packet = []
		self.controller_state = SimpleControllerState()
		
		os.chdir(cwd)
	
	def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
		self.create_inputs(packet.num_cars)
		if self.p_time - packet.game_info.seconds_elapsed < 0:
			self.p_time = packet.game_info.seconds_elapsed
			self.interpreter.send(self.parse(packet, self.game_packet))
			self.interpreter.step()
			return self.get(self.interpreter.recieve())
		else:
			self.p_time = packet.game_info.seconds_elapsed
			return SimpleControllerState()

def get_input(ascii_char=False):
	pass

def on_output(value):
	pass

def on_finish():
	pass

def on_error(error_text):
	print(error_text)

def on_microtick(dot):
	pass
