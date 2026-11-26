#!/usr/bin/env python3
"""Game session manager."""

""""Terminal 1 - initialize game"""
""""ros2 run game_ai game_manager_node"""

""""Terminal 2 - observe sequence"""
""""ros2 topic echo /game/sequence"""

""""Terminal 3 - play game"""
#Start and restart
""""ros2 service call /game/start std_srvs/srv/Trigger "{}" """
#Send sequence
""""ros2 topic pub --once /game/player_input std_msgs/msg/Int32MultiArray "{data: [2]}" """
""""ros2 topic pub --once /game/player_input std_msgs/msg/Int32MultiArray "{data: [2, 4]}" """
"""" ... """
import random, time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Int32MultiArray
from std_srvs.srv import Trigger
from interfaces.msg import AutonomousCommand



class GameManagerNode(Node):
    MAX_STEPS = 20

    def __init__(self):
        super().__init__('game_manager_node')

        self.sequence = []
        self.game_running = False
        self.expected_step = None
        self.performed_step = None
        self.listen_ai_node_for_start = True
        self.ai_predictions = []

        

        # Evaluate player answer.
        self.result_publisher = self.create_publisher(
            Bool, '/game/correct', 10
        )


        # Publish move to do to autonomous node


        self.command_publisher = self.create_publisher(
            AutonomousCommand,
            '/autonomous_command',
            10
        )

        # Get ack from autonomous node

        self.autonomous_ack_subscriber = self.create_subscription(
            AutonomousCommand,
            '/autonomous_command',
            self.check_car_mouvement_performed
        )

        # get start status

        self.start_subs = self.create_subscription(Bool, '/start_game', self.get_start_status)


        """

        # Publish current sequence: [1], [1, 4], [1, 4, 2], ...
        self.sequence_publisher = self.create_publisher(
            Int32MultiArray, '/game/sequence', 10
        )
        """


        """

        # Receive player list
        self.player_subscription = self.create_subscription(
            Int32MultiArray,
            '/game/player_input',
            self.verify_player_sequence,
            10,
        )

        # Starts or restart game.
        self.start_service = self.create_service(
            Trigger, '/game/start', self.start_game
        )
        """

        

        """
        self.ready_publisher = self.create_publisher(
            Bool,
            '/game/ready_for_input',
            10
        )
        """

        
    
    """

    def start_game(self, request, response):
        self.sequence = []
        self.game_running = True
        self.add_move()  # First round generate one move

        response.success = True
        response.message = 'Game started. First sequence published.'
        return response

    def add_move(self):
        # Add one movement to the list.
        move = random.randint(1, 4)
        self.sequence.append(move)

        message = Int32MultiArray()
        message.data = self.sequence.copy()
        self.sequence_publisher.publish(message)

        self.get_logger().info(
            f'Round {len(self.sequence)} - sequence: {self.sequence}'
        )
        self.begin_playback()

    def begin_playback(self):
        self.waiting_for_input = False #CHANGE
        self.playing_sequence = True
        self.playback_index = 0
        self.ready_publisher.publish(Bool(data=False))

        # Publish Moves in Car command
        self.publish_next_move()

    def publish_next_move(self):
        ## Sending the initial sequence is working, 
        ## it does not advance to next movement, due to not yet implemented feedback logic in 
        move = self.sequence[self.playback_index]
        command = AutonomousCommand()
        #command.start = True
        command.move = int(move)
        self.command_publisher.publish(command)
        self.playback_index += 1
        self.get_logger().info(
            f'Playing move {self.playback_index}/{len(self.sequence)}: {move}'
        )

    def verify_player_sequence(self, message):
        # Generate next movement after review
        if not self.game_active:
            self.get_logger().warn('No active game. Call /game/start first.')
            return

        player_input = list(message.data)
        correct = player_input == self.sequence
        self.result_publisher.publish(Bool(data=correct))

        if not correct:
            self.get_logger().warn(
                f'Incorrect sequence: {player_input}. '
                f'Expected {len(self.sequence)} moves. Try again.'
            )
            return  # For now - after will restart the game.

        self.get_logger().info('Correct sequence!')

        if len(self.sequence) >= self.MAX_STEPS:
            self.game_active = False
            self.get_logger().info('Game finished: 20 rounds completed!')
            return

        self.add_move()  # only after right answer.

    """
    # publish towards Screen node if step was correctly done or not

    def publish_step_correctness(self, correctness):

        self.result_publisher.publish(correctness)

    # the callback function for Game launch subscription, store in game_active, communicate with AI node
    # create self.start : bool
    # the topic is published continously in ai_node, this is the reason why we filter with listen_ai_node attrib
    
    def get_ai_launch_status(self, message):

        

        if self.listen_ai_node_for_start:

            self.game_running = message.ai_prediction = 'salut'

        else:

            self.ai_predictions.append(message.ai_prediction)

    # return start attrib, if true, the game should start, else, we do nothing
    
    def check_start():

        return self.game_running


    # callback that store in Node attribute the AI detected movement and, later, in another function, compare to expected movement.
    # create self.ai_move_detected : direction

    def get_performed_move(self, message):        

        self.performed = message.movetype

    # should be call when game launch topic sent from Movement detect Node is set to true
    # generate the sequence to perform
    # send one by one to autonomous node and screen node
    # wait for acknowledgment
    # once all the step is performed by the car and displayed by the screen, publishes the detected movement from AI
    # compare expected step with detected one and publish one the screen whether the player has correctly performed the step or not
    # reapeat all of the above until the last sequence is done 

    def run_game(self):

        self.get_logger().info('Running a game session')



        while(self.game_running):

            self.generate_sequence(4)

            #--SHOW SEQUENCE TO PERFORM------

            for movement in self.sequence:

                self.publish_move_to_perform(movement)
                self.performed = None
                

                while self.performed is None:
                    pass

            #--SHOW SEQUENCE TO PERFORM------


        self.get_logger().info("Ending game session")
    

    # publish on the movement_to_perform topic the move to perform, would be received by Auto and Screen Node
    # move : move to publish

    def publish_move_to_perform(self, move):

        message = AutonomousCommand()
        message.movetype = move
        message.move_done = False

        self.command_publisher.publish()

    # return a new step to append in self.sequence

    def get_step(self):

        return random.randint(1, 4)

    # generate the whole step sequence, call several time get_step fct
    # n : number of step in the sequence

    def generate_sequence(self, n):

        for i in range(n):

            self.sequence.append(get_step())


    # called when autonomous node sent his acknowledgement, then check if move_done is true 


    def check_car_mouvement_performed(self, message):

        if message.movement_done:

            self.performed = self.movetype
            return True

        return False

    
    # clear sequence moves for a new sequence to generate

    def clear_sequence(self):

        self.sequence = []


    # wait for run

    def wait_for_run(self):

        # read game_running value, true or false

        while(not self.check_start()):

            time.sleep(1)

        # launch game 

        self.run_game()

    # function that 

    def get_start_status(self, message):

        self.game_running = message.data
    


def main(args=None):
    rclpy.init(args=args)
    node = GameManagerNode()
    node.get_logger().info('Game manager ready. Send topic /game/start.')

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

    node.wait_for_run()

if __name__ == '__main__':
    main()

