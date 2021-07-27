def get_avg_waiting_time(edge):
    global CURRENT_TIME
    queue = edge.get_occupancy()
    total_waiting_time = 0
    if len(queue) == 0:
        return 0
    for car in queue:
        total_waiting_time += (CURRENT_TIME - car.get_arrival_time())
    avg = float(total_waiting_time) / float(len(queue))
    return avg


def get_max_waiting_time(edge):
    global CURRENT_TIME
    queue = edge.get_occupancy()
    if len(queue) == 0:
        return 0
    return CURRENT_TIME - queue[0].get_arrival_time()


def plot_all(edge, avg_time_quantum, min_q, max_q, stat_type, time_limit, is_poisson=False):
    my_time = [i for i in range(time_limit)]
    for q in range(min_q, max_q):
        y_axis = avg_time_quantum[q]
        plt.legend()
        if is_poisson:
            titl = str(distribution_dict[edge])
            plt.title("lambda = " + titl)
        plt.plot(my_time, y_axis, label=str("line " + str(q)))
    plt.savefig(str(edge.get_origin()) + ' to ' + str(edge.get_destination()) + '_' + stat_type + '.png')
    plt.clf()
    # plt.show()


def stat_avg_quantum():
    global CURRENT_TIME
    global IS_POISSON
    is_poisson = IS_POISSON
    max_q = 20
    min_q = 10
    time_limit = 100
    n = 100
    for e in road_edges_lst:
        avg_time_quantum = np.zeros((max_q, time_limit))
        for q in range(min_q, max_q):
            for i in range(n):
                CURRENT_TIME = 0
                init_distribution_dict()
                init_loss_dict()
                clean_roads()
                for time in range(time_limit):
                    CURRENT_TIME += 1
                    if IS_POISSON:
                        add_poisson_flow()
                        redact_poisson_flow()
                    else:
                        add_rand_flow()
                        redact_rand_flow()
                    switch_lights(q)
                    avg_time_quantum[q][time] += get_avg_waiting_time(e)

        avg_time_quantum = avg_time_quantum / n
        plot_all(e, avg_time_quantum, min_q, max_q, "avg", time_limit, is_poisson)


def stat_max_quantum():
    global CURRENT_TIME
    global IS_POISSON
    is_poisson = IS_POISSON
    max_q = 20
    min_q = 10
    time_limit = 100
    n = 100
    for e in road_edges_lst:
        avg_time_quantum = np.zeros((max_q, time_limit))
        for q in range(min_q, max_q):
            for i in range(n):
                CURRENT_TIME = 0
                init_distribution_dict()
                init_loss_dict()
                clean_roads()
                for time in range(time_limit):
                    CURRENT_TIME += 1
                    if IS_POISSON:
                        add_poisson_flow()
                        redact_poisson_flow()
                    else:
                        add_rand_flow()
                        redact_rand_flow()
                    switch_lights(q)
                    avg_time_quantum[q][time] += get_max_waiting_time(e)

        avg_time_quantum = avg_time_quantum / 100
        plot_all(e, avg_time_quantum, min_q, max_q, "avg", time_limit, is_poisson)

