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
} from "../actions/types";

const initialState = {
    tasks: null
}

export default function(state=initialState, action) {
    switch (action.type) {
        case CANCEL_TASK_SUCCESS:
            return {
                ...state,
                tasks: state.tasks.map(t => t.id === action.payload.taskId ? {...t, status: 'CANCELLED'} : t)
            }
        case ARCHIVATE_TASK_SUCCESS:
            return {
                ...state,
                tasks: state.tasks.map(t => t.id === action.payload.taskId ? {...t, status: 'ARCHIVED'} : t)
            }
        case RESTART_TASK_SUCCESS:
            return {
                ...state,
                tasks: state.tasks.map(t => t.id === action.payload.task.id ? action.payload.task : t)
            }
        case ACCEPT_WORK_SUCCESS:
            return {
                ...state,
                tasks: state.tasks.map(t => t.id === action.payload.taskId ? {...t, status: 'COMPLETED'} : t)
            }
        case TASKS_FETCH_SUCCESS:
            return {
                ...state,
                tasks: action.payload
            }
        case CANCEL_TASK_FAIL:
        case ARCHIVATE_TASK_FAIL:
        case TASKS_FETCH_FAIL:
        case ACCEPT_WORK_FAIL:
        case RESTART_TASK_FAIL:
        default:
            return {...state}
    }
}