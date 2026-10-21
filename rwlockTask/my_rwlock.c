#include "my_rwlock.h"

int my_rwlock_init(my_rwlock_t* lock) {
    
    int err = pthread_mutex_init(&lock->mutex, NULL);
    if (err != 0)
        return err;
    
    err = pthread_cond_init(&lock->readers_cond, NULL);
    if (err != 0) {
        pthread_mutex_destroy(&lock->mutex);
        return err;
    }

    err = pthread_cond_init(&lock->writer_cond, NULL);
    if (err != 0) {
        pthread_mutex_destroy(&lock->mutex);
        pthread_cond_destroy(&lock->readers_cond);
        return err;
    }

    lock->readers_counter = 0;
    lock->wait_read_counter = 0;
    lock->wait_write_counter = 0;
    lock->writer_active = 0;
    
    return 0;
}

int my_rwlock_destroy(my_rwlock_t* lock) {
    pthread_mutex_destroy(&lock->mutex);
    pthread_cond_destroy(&lock->readers_cond);
    pthread_cond_destroy(&lock->writer_cond);

    return 0;
}

int my_rwlock_rdlock(my_rwlock_t* lock) {
    pthread_mutex_lock(&lock->mutex);
    lock->wait_read_counter++;
    while (lock->writer_active || lock->wait_write_counter > 0) {
        pthread_cond_wait(&lock->readers_cond, &lock->mutex);
    }
    lock->wait_read_counter--;
    lock->readers_counter++;
    pthread_mutex_unlock(&lock->mutex);
    return 0;
}

int my_rwlock_wrlock(my_rwlock_t* lock) {
    pthread_mutex_lock(&lock->mutex);
    lock->wait_write_counter++;
    while (lock->writer_active || lock->readers_counter > 0) {
        pthread_cond_wait(&lock->writer_cond, &lock->mutex);
    }
    lock->wait_write_counter--;
    lock->writer_active=1;
    pthread_mutex_unlock(&lock->mutex);
    return 0;
}

int my_rwlock_unlock(my_rwlock_t* lock) {
    pthread_mutex_lock(&lock->mutex);
    
    if(lock->writer_active) {
        lock->writer_active = 0;
    } else {
        lock->readers_counter--;
    }

    if (lock->wait_write_counter > 0) {
        if (!lock->writer_active && lock->readers_counter == 0) {
            pthread_cond_signal(&lock->writer_cond);
        }
    } else {
        pthread_cond_broadcast(&lock->readers_cond);
    }

    pthread_mutex_unlock(&lock->mutex);

    return 0;
}
