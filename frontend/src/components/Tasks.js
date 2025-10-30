import {Link, useParams, useSearchParams} from "react-router-dom";
import {connect} from "react-redux";
import {getTasks, acceptWork, archivateTask, cancelTask, restartTask} from "../actions/tasks";
import {getOffers} from "../actions/offers";
import {useEffect} from "react";
import {Badge, Button, Skeleton, Table, Tabs, Tag} from "antd";
import '../styles/Tasks.css';

const taskStatus = {
    ATWORK: {
        text: 'В работе',
        status: 'success'
    },
    ACCEPTSOFFERS: {
        text: 'В поисках исполнителя',
        status: 'warning'
    },
    ARCHIVED: {
        text: 'Архивирован',
        status: 'default'
    },
    SUBMITTED: {
        text: 'На проверке',
        status: 'warning'
    },
    COMPLETED: {
        text: 'Завершен',
        status: 'success'
    },
    CANCELLED: {
        text: 'Отменен',
        status: 'error'
    }
}

const getTaskControl = (task, onAcceptClick, onCancelClick, onRestartClick, onArchivateClick) => {
    if (task.status === 'ACCEPTSOFFERS') {
        return [
            <Button type={'dashed'} onClick={() => onArchivateClick(task)}>В архив</Button>
        ]
    } else if (task.status === 'ARCHIVED' || task.status === 'CANCELLED') {
        return [
            <Button
                type={"primary"}
                title={'Нажмите, чтобы снова опубликовать заказ'}
                onClick={() => onRestartClick(task)}
            >Перезапустить</Button>
        ]
    } else if (task.status === 'SUBMITTED') {
        return (
            <div className={'control-task'}>
                <Button
                    type={'primary'}
                    style={{backgroundColor: '#4fc206'}}
                    onClick={() => onAcceptClick(task)}
                >Принять работу</Button>
                <br></br>
                <Button type={'primary'} danger onClick={() => onCancelClick(task)}>Отменить</Button>
            </div>
        )
    } else if (task.status === 'ATWORK') {
        return (
            <div className={'control-task'}>
                <Button type={'primary'} danger onClick={() => onCancelClick(task)}>Отменить</Button>
                <Button
                    type={'primary'}
                    danger
                    title={'Нажмите, чтобы отменить и снова опубликовать заказ и найти нового исполнителя'}
                    onClick={() => {
                        onCancelClick(task);
                        onRestartClick(task);
                    }}
                >Отменить и перезапустить</Button>
            </div>
        )
    }
}

function Tasks ({ getOffers, getTasks, acceptWork, archivateTask, cancelTask, restartTask, tasks, offers }) {
    const params = useParams();
    const [searchParams, setSearchParams] = useSearchParams();

    useEffect(() => {
        const fetchOffers = async () => {
            await getOffers(searchParams);
        }
        const fetchTasks = async () => {
            await getTasks(searchParams);
        }
        if (tasks === null) {
            fetchTasks();
        }
        if (offers === null) {
            fetchOffers();
        }
    });

    if (tasks === null || offers === null) {
        return <Skeleton active/>
    }

    const onAcceptClick = (task) => {
        console.log('ACCEPT WORK BUTTON CLICKED')
        acceptWork(task, searchParams);
    }
    const onCancelClick = (task) => {
        console.log('CANCEL TASK BUTTON CLICKED')
        cancelTask(task, searchParams);
    }
    const onRestartClick = (task) => {
        console.log('RESTART TASK BUTTON CLICKED')
        restartTask(task, searchParams);
    }
    const onArchivateClick = (task) => {
        console.log('ARCHIVATE TASK BUTTON CLICKED')
        archivateTask(task, searchParams);
    }
    console.log(offers)
    const columns = [
        {
            title: 'Название',
            dataIndex: 'title',
            key: 'title',
            render: (text, record) => <Link to={`/task/${record.id}?token=${searchParams.get('token')}`}><p><i>{record.title.substring(0, 50)}{record.title.length > 50 ? '...' : null}</i></p></Link>
        },
        {
            title: 'Бюджет',
            key: 'budget',
            render: (text, record) => {
                console.log(record)
                let budget = null;
                if (record.budget_from !== null) {
                    budget = `от ${record.budget_from} до ${record.budget_to} ₽`
                } else if (record.budget !== null) {
                    budget = `${record.budget} ₽`
                } else {
                    budget = 'По договору'
                }
                return <p className={'task-price'}>{budget}</p>
            }
        },
        {
            title: 'Дедлайн',
            key: 'deadline',
            render: (text, record) => <p>{record.deadline} дн.</p>
        },
        {
            title: 'Описание',
            dataIndex: 'description',
            key: 'description',
            render: (text, record) => <p><i>{record.description.substring(0, 60)}{record.description.length > 60 ? '...' : null}</i></p>
        },
        {
            title: 'Время публикации',
            key: 'created_at',
            render: (text, record) => record.created_at.split('.')[0].replace('T', ' ')
        },
        {
            title: 'Теги',
            dataIndex: 'tags',
            key: 'tags',
            render: (text, record) => record.tags.map((t) => <Tag>{t}</Tag>)
        },
        {
            title: 'Статус',
            key: 'status',
            render: (text, record) => <Badge status={taskStatus[record.status].status} text={taskStatus[record.status].text}/>
        },
        {
            title: 'Необработанные отклики / Все отклики',
            key: 'offers_count',
            render: (text, record) => <Link to={`/offers?token=${searchParams.get('token')}&task_id=${record.id}`}>{record.pending_offers_count} / {record.offers_count}</Link>
        },
        {
            title: '',
            key: 'control-task',
            render: (text, record) => getTaskControl(record, onAcceptClick, onCancelClick, onRestartClick, onArchivateClick)
        }
    ]
    const taskTabs = [
        {
            key: 'actual',
            label: 'Актуальные',
            children: <Table dataSource={tasks.filter(t => t.status === 'ACCEPTSOFFERS')} columns={columns}/>
        },
        {
            key: 'submitted',
            label: 'На проверке',
            children: <Table dataSource={tasks.filter(t => t.status === 'SUBMITTED')} columns={columns}/>
        },
        {
            key: 'atwork',
            label: 'В работе',
            children: <Table dataSource={tasks.filter(t => t.status === 'ATWORK')} columns={columns}/>
        },
        {
            key: 'completed',
            label: 'Завершенные',
            children: <Table dataSource={tasks.filter(t => t.status === 'COMPLETED')} columns={columns}/>
        },
        {
            key: 'archived',
            label: 'Архив',
            children: <Table dataSource={tasks.filter(t => t.status === 'ARCHIVED')} columns={columns}/>
        },
        {
            key: 'cancelled',
            label: 'Отмененные',
            children: <Table dataSource={tasks.filter(t => t.status === 'CANCELLED')} columns={columns}/>
        }
    ]
    let defaultKey = null;
    if (tasks.filter(t => t.status === 'SUBMITTED').length > 0) defaultKey = 'submitted'
    else if (tasks.filter(t => t.status === 'ATWORK').length > 0) defaultKey = 'atwork'
    else defaultKey = 'actual'

    return (
        <div>
            <Tabs items={taskTabs} defaultActiveKey={defaultKey}/>
        </div>
    )
}

const mapStateToProps = state => ({
    tasks: state.tasks.tasks,
    offers: state.offers.offers
});

export default connect(mapStateToProps, { getOffers, getTasks, acceptWork, archivateTask, cancelTask, restartTask })(Tasks);