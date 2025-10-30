import {
    OFFER_ACCEPT_FAIL,
    OFFER_ACCEPT_SUCCESS,
    OFFER_REJECT_FAIL,
    OFFER_REJECT_SUCCESS,
    OFFERS_FETCH_FAIL,
    OFFERS_FETCH_SUCCESS
} from "../actions/types";

const initialState = {
    offers: null
}

export default function(state=initialState, action) {
    switch (action.type) {
        case OFFER_ACCEPT_SUCCESS:
            return {
                ...state,
                offers: state.offers.map(o => o.id === action.payload.offerId ? {...o, status: 'ACCEPTED'} : o)
            }
        case OFFER_REJECT_SUCCESS:
            return {
                ...state,
                offers: state.offers.map(o => o.id === action.payload.offerId ? {...o, status: 'REJECTED'} : o)
            }
        case OFFERS_FETCH_SUCCESS:
            return {
                ...state,
                offers: action.payload
            }
        case OFFERS_FETCH_FAIL:
        case OFFER_REJECT_FAIL:
        case OFFER_ACCEPT_FAIL:
        default:
            return state
    }
}