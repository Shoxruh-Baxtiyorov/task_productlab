import {
    ACCEPT_WORK_FAIL,
    ACCEPT_WORK_SUCCESS,
    ARCHIVATE_TASK_FAIL,
    ARCHIVATE_TASK_SUCCESS,
    CANCEL_TASK_FAIL,
    CANCEL_TASK_SUCCESS,
    RESTART_TASK_FAIL,
    RESTART_TASK_SUCCESS,
    TASKS_FETCH_FAIL,
    TASKS_FETCH_SUCCESS
} from "./types";
import axios from "axios";

export const archivateTask = (task, qparams) => async dispatch => {
    const config = {
        params: {
            token: qparams.get('token'),
            task_id: task.id,
        }
    }

    if (config.params.token === null) {
        // TODO: unauthorized
        dispatch({
            type: ARCHIVATE_TASK_FAIL
        });
    }

    try {
        const res = await axios.post(`${process.env.REACT_APP_DTASKBOT_API_URL}/tasks/client/${task.id}/archive`, null, config)

        if (res.status === 200) {
            dispatch({
                type: ARCHIVATE_TASK_SUCCESS,
                payload: {taskId: task.id}
            });
        } else {
            console.log(`CANNOT ARCHIVATE TASK. STATUS: ${res.status}`)
            dispatch({
                type: ARCHIVATE_TASK_FAIL
            });
        }
    } catch (err) {
        console.log(`ERROR WHILE ARCHIVATING TASK ${err}`)
        if (err.response.status === 401) {
            // TODO: handle 401
        }
        dispatch({
            type: ARCHIVATE_TASK_FAIL
        });
    }
}

export const restartTask = (task, qparams) => async dispatch => {
    const config = {
        params: {
            token: qparams.get('token')
        }
    }

    if (config.params.token === null) {
        // TODO: unauthorized
        dispatch({
            type: RESTART_TASK_FAIL
        });
    }

    try {
        const res = await axios.post(`${process.env.REACT_APP_DTASKBOT_API_URL}/tasks/client/${task.id}/republish`, null, config)

        if (res.status === 200) {
            console.log('yes', res.data)
            dispatch({
                type: RESTART_TASK_SUCCESS,
                payload: {task: res.data.task}
            });
        } else {
            console.log(`CANNOT RESTART TASK. STATUS: ${res.status}`)
            dispatch({
                type: RESTART_TASK_FAIL
            });
        }
    } catch (err) {
        console.log(`ERROR WHILE RESTARTING TASK ${err}`)
        if (err.response.status === 401) {
            // TODO: handle 401
        }
        dispatch({
            type: RESTART_TASK_FAIL
        });
    }
}

export const cancelTask = (task, qparams) => async dispatch => {
    const config = {
        params: {
            token: qparams.get('token'),
            task_id: task.id,
        }
    }

    if (config.params.token === null) {
        // TODO: unauthorized
        dispatch({
            type: CANCEL_TASK_FAIL
        });
    }

    try {
        const res = await axios.post(`${process.env.REACT_APP_DTASKBOT_API_URL}/tasks/client/${task.id}/cancel`, null, config)

        if (res.status === 200) {
            dispatch({
                type: CANCEL_TASK_SUCCESS,
                payload: {taskId: task.id}
            });
        } else {
            console.log(`CANNOT CANCEL TASK. STATUS: ${res.status}`)
            dispatch({
                type: CANCEL_TASK_FAIL
            });
        }
    } catch (err) {
        console.log(`ERROR WHILE CANCELLING TASK ${err}`)
        if (err.response.status === 401) {
            // TODO: handle 401
        }
        dispatch({
            type: CANCEL_TASK_FAIL
        });
    }
}

export const acceptWork = (task, qparams) => async dispatch => {
    const config = {
        params: {
            token: qparams.get('token'),
            task_id: task.id,
        }
    }

    if (config.params.token === null) {
        // TODO: unauthorized
        dispatch({
            type: ACCEPT_WORK_FAIL
        });
    }

    try {
        const res = await axios.post(`${process.env.REACT_APP_DTASKBOT_API_URL}/tasks/client/${task.id}/accept`, null, config)

        if (res.status === 200) {
            dispatch({
                type: ACCEPT_WORK_SUCCESS,
                payload: {taskId: task.id}
            });
        } else {
            console.log(`CANNOT ACCEPT WORK. STATUS: ${res.status}`)
            dispatch({
                type: ACCEPT_WORK_FAIL
            });
        }
    } catch (err) {
        console.log(`ERROR WHILE ACCEPTING TASK WORK ${err}`)
        if (err.response.status === 401) {
            // TODO: handle 401
        }
        dispatch({
            type: ACCEPT_WORK_FAIL
        });
    }
}

export const getTasks = (qparams) => async dispatch => {
    const config = {
        params: {
            token: qparams.get('token'),
            tags: qparams.get('tags'),
            archived: true,
            offset: qparams.get('offset'),
            limit: qparams.get('limit')
        }
    }

    if (config.params.token === null) {
        // TODO: unauthorized
        dispatch({
            type: TASKS_FETCH_FAIL
        });
    }

    try {
        const res = await axios.get(`${process.env.REACT_APP_DTASKBOT_API_URL}/tasks/client`, config)

        if (res.status === 200) {
            dispatch({
                type: TASKS_FETCH_SUCCESS,
                payload: res.data
            });
        } else {
            console.log(`CANNOT FETCH OFFERS. STATUS: ${res.status}`)
            dispatch({
                type: TASKS_FETCH_FAIL
            });
        }
    } catch (err) {
        console.log(`ERROR WHILE FETCHING OFFERS ${err}`)
        if (err.response.status === 401) {
            // TODO: handle 401
        }
        dispatch({
            type: TASKS_FETCH_FAIL
        });
    }
}