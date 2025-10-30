import {GET_ME_REQUEST, GET_ME_FAIL, GET_ME_SUCCESS} from "../actions/types";

const initialState = {
    user: null,
    error: null,
    loading: false
}

export default function(state=initialState, action) {
    switch (action.type) {
        case GET_ME_REQUEST:
            return {
                ...state,
                loading: true,
                error: null
            }
        case GET_ME_SUCCESS:
            return {
                ...state,
                user: action.payload,
                error: null,
                loading: false
            }
        case GET_ME_FAIL:
            return {
                ...state,
                user: null,
                error: "Ошибка загрузки профиля",
                loading: false
            }
        default:
            return {...state}
    }
}