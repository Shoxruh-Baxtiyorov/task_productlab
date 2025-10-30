import {useParams, useSearchParams} from "react-router-dom";
import {connect} from "react-redux";
import {getOffers, rejectOffer, acceptOffer} from "../actions/offers";
import {getTasks} from "../actions/tasks";
import {useEffect} from "react";
import {Avatar, Button, Select, Skeleton, Table, Tabs} from "antd";
import {Link} from "react-router-dom";
import {Badge} from "antd";
import '../styles/Offers.css'
import {UserOutlined} from "@ant-design/icons";

const offerStatus = {
    SAMPLED: {
        text: 'В выборке',
        status: 'warning'
    },
    PENDING: {
        text: 'Ожидает ответа',
        status: 'processing'
    },
    REJECTED: {
        text: 'Отклонен',
        status: 'error'
    },
    ACCEPTED: {
        text: 'Принят',
        status: 'success'
    },
}

const getOfferControls = (offer, onRejectClick, onAcceptClick) => {
    if (offer.status !== 'REJECTED' && offer.status !== 'ACCEPTED') {
        return (
            <div className={'control-offer'}>
                <Button
                    type={'primary'}
                    style={{backgroundColor: '#4fc206'}}
                    onClick={() => onAcceptClick(offer)}>Принять</Button>
                <br/>
                <Button
                    type={'primary'}
                    danger
                    onClick={() => onRejectClick(offer)}>Отклонить</Button>
            </div>
        )
    }
}

function Offers ({ getOffers, rejectOffer, acceptOffer, getTasks, offers }) {
    const params = useParams();
    const [searchParams, setSearchParams] = useSearchParams();
    const taskId = searchParams.get('task_id');

    useEffect(() => {
        const fetchOffers = async () => {
            await getOffers(searchParams);
        }
        if (offers === null) {
            fetchOffers();
        }
    });

    const onAcceptClick = (offer) => {
        console.log('accepted', offer)
        acceptOffer(offer, searchParams)
        getTasks(searchParams)
    }

    const onRejectClick = (offer) => {
        console.log('rejected', offer)
        rejectOffer(offer, searchParams)
    }

    if (offers === null) {
        return <Skeleton active/>
    }

    if (taskId) {
        offers = offers.filter(o => o.task.id === parseInt(taskId))
    }
    
    const columns = [
        {
            title: 'Исполнитель',
            dataIndex: ['author', 'full_name'],
            key: 'name',
            render: (text, record) => {
                const phone = record.author.phone.startsWith('+') ? record.author.phone : `+${record.author.phone}`
                let contactInfo = <div id={'phone'}>{phone}</div>
                if (record.author.username != null) {
                    contactInfo = <div id={'contact'}>{contactInfo}, <div id={'username'}><a href={`https://t.me/${record.author.username}`} target={'_blank'}>@{record.author.username}</a></div></div>
                }
                return (
                    <div className={'offer-freelancer'}>
                        <Avatar size={32} icon={<UserOutlined/>}/>
                        <div className={'offer-freelancer-contact'}>
                            <b>{record.author.full_name}</b>
                            <br></br>
                            {contactInfo}
                            <p style={{color: '#4fc206'}}>{record.budget}₽, {record.deadline_days} дней</p>
                        </div>
                    </div>
                )
            }
        },
        {
            title: 'Заказ',
            dataIndex: ['task', 'title'],
            key: 'task',
            render: (text, record) => <Link to={`/tasks?token=${searchParams.get('token')}&task_id=${record.task.id}`}>{text}</Link>
        },
        {
            title: 'Отклик',
            dataIndex: 'description',
            key: 'description',
            render: (text, record) => <Link to={`/offer/${record.id}?token=${searchParams.get('token')}`}><p><i>{record.description.substring(0, 150)}{record.description.length > 150 ? '...' : null}</i></p></Link>
        },
        {
            title: 'Статус',
            dataIndex: 'status',
            key: 'status',
            render: (text, record) => <Badge status={offerStatus[record.status].status} text={offerStatus[record.status].text}/>
        },
        {
            title: 'Выполнено задач',
            dataIndex: 'completed_tasks_count',
            key: 'completed_tasks_count',
            render: (text, record) => record.author.completed_tasks_count
        },
        {
            title: 'Windows клиент',
            dataIndex: ['author', 'has_windows_client'],
            key: 'has_windows_client',
            render: (text, record) => <Badge status={record.author.has_windows_client ? 'success' : 'warning'} text={record.author.has_windows_client ? 'Есть' : 'Отсутствует'}/>
        },
        {
            title: '',
            dataIndex: 'change-status',
            key: 'change-status',
            render: (text, record) => getOfferControls(record, onRejectClick, onAcceptClick)
        }
    ]

    const offersTabs = [
        {
            key: 'actual',
            label: 'Актуальные',
            children: [
                <Link to={`/messenger?token=${searchParams.get('token')}&task_id=${taskId}`}>Перейти в диалоги</Link>,
                <Table
                    dataSource={offers.filter(o => o.status !== 'REJECTED')}
                    columns={columns}
                />
            ]
        },
        {
            key: 'rejected',
            label: 'Отклоненные',
            children: <Table
                dataSource={offers.filter(o => o.status === 'REJECTED')}
                columns={columns}
            />
        }
    ]

    return (
        <div>
            <Tabs items={offersTabs} defaultActiveKey={'actual'}/>
        </div>
    )
}

const mapStateToProps = state => ({
    offers: state.offers.offers
});

export default connect(mapStateToProps, { getOffers, rejectOffer, acceptOffer, getTasks })(Offers);