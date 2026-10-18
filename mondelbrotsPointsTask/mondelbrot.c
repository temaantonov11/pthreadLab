#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "../shared_libs/my_rand.h"
#include "../shared_libs/timer.h"

#define N 1000
#define X_LEFT_BOUND -2
#define X_RIGHT_BOUND 0.5
#define Y_LEFT_BOUND -1.12
#define Y_RIGHT_BOUND 1.12

int nthreads;
int npoints;

typedef struct {
    double x;
    double y;
} point_t;

point_t* points;

void* routine(void* rank) {
    long my_rank = (long)rank;

    unsigned seed = 1 + my_rank;

    int n_points = npoints / nthreads + (my_rank < npoints % nthreads ? 1 : 0);
    int start_index = my_rank * (npoints / nthreads) + (my_rank < npoints % nthreads ? my_rank : npoints % nthreads);

    int finded_points = 0;

    while (finded_points < n_points) {

        double x = 0.0, y = 0.0;
        double x_new, y_new;
        int montelbort_flag = 0;

        double a,b;

        a = X_LEFT_BOUND + my_drand(&seed)*(X_RIGHT_BOUND - X_LEFT_BOUND);
        b = Y_LEFT_BOUND + my_drand(&seed)*(Y_RIGHT_BOUND - Y_LEFT_BOUND);

        for (int j = 0; j < N; j++) {

            x_new = x*x - y*y + a;
            y_new = 2*x*y + b;
            x = x_new;
            y = y_new;

            if (x*x + y*y > 4){
                montelbort_flag = 1;
                break;
            }
        }

        if (montelbort_flag == 0) {
            point_t point = {a, b};
            points[start_index + finded_points] = point;
            finded_points++;
        }
    }
    return NULL;
}

int main(int argc, char** argv) {
    nthreads = strtol(argv[1], NULL, 10);
    npoints = strtol(argv[2], NULL, 10);
    
    double start, end;

    pthread_t* thread_handles = malloc(nthreads * sizeof(pthread_t));
    points = malloc(npoints * sizeof(point_t));

    GET_TIME(start);
    for (int i = 0; i < nthreads; i++) {
        int err = pthread_create(&thread_handles[i], NULL, routine, (void*)i);

        if (err != 0) {
            perror("Failed creating thread");
        }
    }

    for (int i = 0; i < nthreads; i++) {
        pthread_join(thread_handles[i], NULL);
    }
    GET_TIME(end);

    FILE *file = fopen("results.csv", "w");

    for (int i = 0; i < npoints; i++) {
        fprintf(file, "%.6f,%.6f\n", points[i].x, points[i].y);
    }

    printf("%f\n", end - start);

    fclose(file);
    free(thread_handles);
    free(points);
}