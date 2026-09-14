/**********************
*
*This is a manual mountain car(t) with physics, no visuals, no keyboard
*Created 2026 by Daniel Goehring
*Comes with a precoded policy, no learning algorithm implemented yet
*Todo: Non-deterministic physics, e.g., gaussian, multi agents
*
*
***********************/


#include <iostream>
#include <cmath>

const int WINDOW_WIDTH = 1024;
const double MOUNTAIN_HEIGHT = 256.0;
const double HORIZONTAL_SCALE_FACTOR = 2*M_PI/WINDOW_WIDTH;
const double MAX_ABS_ACCELERATION = 0.75;
const int MAX_STEPS_PER_EPISODE = 1000;
const int MAX_EPISODES = 200000;
const bool VERBOSE = true;


double p = 0;
double v = 0;
int episodes = 0;
int steps = 0;
double reward = 0;
int action = 0;
int trunc_or_term = 0;
int running = true;


double mountain_derivative(double x)
{
    return  -MOUNTAIN_HEIGHT * sin(HORIZONTAL_SCALE_FACTOR*x);
}


void update_state() {
    //this calculates the height and ascent on the mountain
    double d = mountain_derivative(p);
	
	trunc_or_term = 0;
    reward = 0;
	
    //action leads to increased / decreased velocity
    v = v + action * MAX_ABS_ACCELERATION;


    //velocity update by gravitational force
    v = v - sin(atan(d));

    //velocity update with viscous friction force
    v = v * 0.995;

    //position update
    p = p + v/5;

    if (p > WINDOW_WIDTH) {
        reward = 100;
        if (VERBOSE) {
            std::cout << "SUCCESS, required steps: " << steps << " resetting 01";
		}

        p = M_PI / HORIZONTAL_SCALE_FACTOR;  //start at center
        v = 0; //positive reward
        steps = 0;
        trunc_or_term = 1;
	}

    else if (p <= 0) {
        reward = -1; //-100
        //print("FELL OF LEFT CLIFF, required steps: ", steps, " resetting 02")
        p = 0;  //math.pi / HORIZONTAL_SCALE_FACTOR
        v = 0;  //negative reward
        //steps = 0
        trunc_or_term = 0;  //1
	}
    else {
        if (steps > MAX_STEPS_PER_EPISODE) {
            if (VERBOSE) {
              //  print("TOO MANY STEPS, ", steps, "  resetting 03");
			}
            p = M_PI / HORIZONTAL_SCALE_FACTOR;
            v = 0;
            steps = 0;
            trunc_or_term = 2;
        reward = -1;
		}
	}


    // needs to add value
    return;
}

void agent_request() {

    //BASELINE policy:
    if (v >= -1) {
        action = 1;
    }
    else {
        action = -1;
    }
    //
    //here comes the state transition model, simple physics
    update_state();

    return;
}


int main() {
	running = true;

    //start position
    p = M_PI / HORIZONTAL_SCALE_FACTOR; //start at the valley

    //start velocity
    v = 0;

    episodes = 0;
    steps = 0;

    while (running) {
        //SWITCH THIS ONE OFF FOR FAST SIMULATION or ON for real physics
      
		steps = steps + 1;

        if (VERBOSE) {
            if (steps % 100 == 0) {
                std::cout << "Episode: " << episodes << " Step: " << steps;
			}
		}
    
		agent_request();

        if (trunc_or_term !=0) {
            episodes += 1;
            if (VERBOSE) {
               // print("Episode: ", episodes, " FINISHED ");
			}
		}
		
        if (episodes >= MAX_EPISODES) {
            running = false;
		}
	
	}

	return 0;
}
