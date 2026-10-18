#include <pthread.h>


typedef struct {
    pthread_mutex_t mutex;

    pthread_cond_t readers_cond;
    pthread_cond_t writer_cond;

    int readers_counter;

    int wait_read_counter;
    int wait_write_counter;

    int writer_active;

} my_rwlock_t;

int my_rwlock_init(my_rwlock_t* lock);
int my_rwlock_destroy(my_rwlock_t* lock);

int my_rwlock_rdlock(my_rwlock_t* lock);
int my_rwlock_wrlock(my_rwlock_t* lock);

int my_rwlock_unlock(my_rwlock_t* lock);